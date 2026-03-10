from typing import Dict, Any, List, Optional, Type
import logging
import os
import ssl
import json
import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Tool as MCPTool

from langchain_core.tools import BaseTool, StructuredTool
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel, Field, create_model

from src.core.ports.mcp_client_port import MCPClientPort


def _json_schema_to_pydantic_model(name: str, schema: dict) -> Type[BaseModel]:
    """
    Convierte un JSON Schema a un modelo Pydantic dinámico.
    
    Args:
        name: Nombre del modelo
        schema: JSON Schema con properties y required
        
    Returns:
        Clase Pydantic generada dinámicamente
    """
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    
    fields = {}
    for field_name, field_schema in properties.items():
        field_type = _json_type_to_python(field_schema.get("type", "string"))
        description = field_schema.get("description", "")
        default = ... if field_name in required else None
        
        fields[field_name] = (field_type, Field(default=default, description=description))
    
    return create_model(name, **fields)


def _json_type_to_python(json_type: str) -> type:
    """Mapea tipos JSON Schema a tipos Python."""
    type_map = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    return type_map.get(json_type, str)


class MCPClientAdapter(MCPClientPort):
    """
    Adaptador MCP usando el SDK oficial con transporte HTTP streamable.
    
    Ventajas sobre langchain-mcp-adapters:
    - Control total del cliente httpx (SSL, timeouts, headers)
    - Sin dependencias pesadas de LangChain
    - SDK oficial mantenido por Anthropic
    """
    
    # Ruta del bundle de CA del sistema (contenedores Linux)
    SYSTEM_CA_BUNDLE = "/etc/ssl/certs/ca-certificates.crt"
    
    def _init_(
        self, 
        server_url: str, 
        server_name: str = "default",
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ):
        """
        Inicializa el adaptador MCP.
        
        Args:
            server_url: URL del servidor MCP (debe soportar HTTP streamable)
            server_name: Nombre identificador para logging
            timeout: Timeout en segundos para las peticiones HTTP
            verify_ssl: Si True, verifica certificados SSL
        """
        self.server_url = server_url
        self.server_name = server_name
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        self._session: Optional[ClientSession] = None
        self._tools: Optional[List[MCPTool]] = None
        self._tools_map: Dict[str, MCPTool] = {}
        self._langchain_tools: Optional[List[BaseTool]] = None
        self._context_stack = None
        
        self.logger = logging.getLogger(f"{_name_}.MCPClientAdapter")
    
    def _get_ssl_context(self) -> ssl.SSLContext | bool:
        """
        Obtiene el contexto SSL apropiado.
        
        Usa el bundle de CA del sistema si existe (para CAs privadas),
        de lo contrario usa el default de Python.
        """
        if not self.verify_ssl:
            return False
        
        if os.path.exists(self.SYSTEM_CA_BUNDLE):
            ctx = ssl.create_default_context(cafile=self.SYSTEM_CA_BUNDLE)
            self.logger.debug(f"Usando CA bundle del sistema: {self.SYSTEM_CA_BUNDLE}")
            return ctx
        
        return True  # Usa el default de Python/certifi
    
    async def _initialize_client(self) -> None:
        """
        Inicializa la sesión MCP si no está inicializada.
        """
        if self._session is not None:
            return
        
        # Validar URL
        if not self.server_url:
            self.logger.warning(
                f"URL no configurada para servidor MCP: {self.server_name}"
            )
            self._tools = []
            self._tools_map = {}
            return
        
        self.logger.info(
            f"Inicializando MCP client para servidor: {self.server_name} "
            f"con URL: {self.server_url}"
        )
        
        try:
            # Crear factory de httpx con SSL configurado
            ssl_context = self._get_ssl_context()
            
            # En mcp==1.23.0, streamablehttp_client acepta httpx_client_factory:
            def _custom_httpx_factory(
                headers: dict[str, str] | None = None,
                timeout: httpx.Timeout | None = None,
                auth: httpx.Auth | None = None,
            ) -> httpx.AsyncClient:
                """Factory que inyecta verify=ssl_context en el AsyncClient."""
                kwargs: dict[str, Any] = {
                    "verify": ssl_context,
                    "follow_redirects": True,
                }
                if headers is not None:
                    kwargs["headers"] = headers
                if timeout is not None:
                    kwargs["timeout"] = timeout
                if auth is not None:
                    kwargs["auth"] = auth
                self.logger.debug(
                    f"Creando httpx.AsyncClient con headers={list(headers.keys()) if headers else None}, "
                    f"timeout={timeout}, verify={type(ssl_context)._name_}"
                )
                return httpx.AsyncClient(**kwargs)
            
            # streamablehttp_client devuelve (read_stream, write_stream, get_session_id)
            self._context_stack = streamablehttp_client(
                url=self.server_url,
                httpx_client_factory=_custom_httpx_factory,
            )
            
            # Entrar al context manager
            streams = await self.context_stack.aenter_()
            read_stream, write_stream, _ = streams
            
            # Crear la sesión del cliente
            self._session = ClientSession(read_stream, write_stream)
            await self.session.aenter_()
            
            # Inicializar el protocolo MCP
            await self._session.initialize()
            
            # Obtener herramientas
            self.logger.info(f"Obteniendo herramientas del servidor MCP: {self.server_name}")
            tools_result = await self._session.list_tools()
            self._tools = tools_result.tools
            self._tools_map = {tool.name: tool for tool in self._tools}
            
            self.logger.info(
                f"Cargadas {len(self._tools)} herramientas desde "
                f"servidor MCP: {self.server_name}"
            )
            
        except BaseException as e:
            # Capturar BaseException para incluir CancelledError de asyncio/anyio
            import traceback
            self.logger.error(
                f"Error al inicializar MCP client para {self.server_name}: {str(e)}"
            )
            self.logger.debug(traceback.format_exc())
            self._tools = []
            self._tools_map = {}
            self._langchain_tools = []
            await self._cleanup()
            # No lanzar excepción, solo loguear y continuar con tools vacías
            # Esto permite que el agente funcione sin las herramientas MCP
            self.logger.warning(
                f"MCP client para {self.server_name} no disponible. "
                f"El agente funcionará sin herramientas MCP."
            )
    
    async def _cleanup(self) -> None:
        """Limpia recursos de la sesión."""
        if self._session:
            try:
                await self.session.aexit_(None, None, None)
            except Exception:
                pass
            self._session = None
        
        if self._context_stack:
            try:
                await self.context_stack.aexit_(None, None, None)
            except Exception:
                pass
            self._context_stack = None
    
    def _convert_mcp_tool_to_langchain(self, mcp_tool: MCPTool) -> BaseTool:
        """
        Convierte una herramienta MCP a una LangChain BaseTool.
        
        Args:
            mcp_tool: Herramienta del SDK MCP
            
        Returns:
            BaseTool compatible con LangChain/LangGraph
        """
        # Capturar referencia a self para el closure
        adapter = self
        tool_name = mcp_tool.name
        
        # Crear modelo de args dinámicamente desde el inputSchema
        input_schema = mcp_tool.inputSchema if hasattr(mcp_tool, 'inputSchema') else {}
        if isinstance(input_schema, dict):
            args_schema = _json_schema_to_pydantic_model(
                f"{mcp_tool.name}Args",
                input_schema
            )
        else:
            # Schema vacío por defecto
            args_schema = create_model(f"{mcp_tool.name}Args")
        
        async def _arun(**kwargs) -> str:
            """Ejecuta la herramienta MCP de forma asíncrona."""
            result = await adapter._session.call_tool(tool_name, kwargs)
            
            # Extraer contenido del resultado
            if result.content:
                contents = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        contents.append(content.text)
                    elif hasattr(content, 'data'):
                        contents.append(str(content.data))
                return contents[0] if len(contents) == 1 else json.dumps(contents)
            return ""
        
        def _run(**kwargs) -> str:
            """No soportado - usar versión async."""
            raise NotImplementedError("Use la versión async de esta herramienta")
        
        # Crear StructuredTool con el schema generado
        return StructuredTool(
            name=mcp_tool.name,
            description=mcp_tool.description or f"Tool: {mcp_tool.name}",
            args_schema=args_schema,
            func=_run,
            coroutine=_arun,
        )
    
    async def get_tools(self) -> List[BaseTool]:
        """
        Obtiene las herramientas disponibles desde el servidor MCP
        convertidas a LangChain BaseTool.
        
        Returns:
            Lista de herramientas compatibles con LangChain/LangGraph
        """
        try:
            if self._tools is None:
                await self._initialize_client()
            
            # Convertir tools MCP a LangChain si no lo hemos hecho
            if self._langchain_tools is None and self._tools:
                self._langchain_tools = [
                    self._convert_mcp_tool_to_langchain(tool) 
                    for tool in self._tools
                ]
                self.logger.info(
                    f"Convertidas {len(self._langchain_tools)} herramientas MCP "
                    f"a LangChain tools para: {self.server_name}"
                )
            
            return list(self._langchain_tools) if self._langchain_tools else []
        except BaseException as e:
            # Capturar BaseException para incluir CancelledError
            self.logger.error(
                f"Error obteniendo herramientas del servidor MCP "
                f"{self.server_name}: {str(e)}"
            )
            return []
    
    async def get_raw_mcp_tools(self) -> List[MCPTool]:
        """
        Obtiene las herramientas MCP sin convertir (para uso directo con SDK MCP).
        
        Returns:
            Lista de herramientas MCP nativas (mcp.types.Tool)
        """
        try:
            if self._tools is None:
                await self._initialize_client()
            return list(self._tools) if self._tools else []
        except Exception as e:
            self.logger.error(
                f"Error obteniendo herramientas MCP raw: {str(e)}"
            )
            return []
    
    async def execute_tool(
        self, 
        tool_name: str, 
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta una herramienta específica en el servidor MCP.
        
        Args:
            tool_name: Nombre de la herramienta a ejecutar
            tool_input: Parámetros de entrada para la herramienta
            
        Returns:
            Diccionario con 'result' si éxito o 'error' si falla
        """
        try:
            if self._session is None:
                await self._initialize_client()
            
            if not self._tools_map:
                self.logger.warning(
                    f"No hay herramientas disponibles para servidor MCP "
                    f"{self.server_name}"
                )
                return {
                    "error": f"No hay herramientas disponibles para "
                             f"servidor MCP {self.server_name}"
                }
            
            if tool_name not in self._tools_map:
                self.logger.warning(
                    f"Herramienta {tool_name} no encontrada en servidor MCP "
                    f"{self.server_name}"
                )
                return {
                    "error": f"Herramienta {tool_name} no encontrada en "
                             f"servidor MCP {self.server_name}"
                }
            
            self.logger.info(
                f"Ejecutando herramienta {tool_name} en servidor MCP "
                f"{self.server_name}"
            )
            
            # Llamar a la herramienta usando el protocolo MCP
            result = await self._session.call_tool(tool_name, tool_input)
            
            self.logger.info(f"Herramienta {tool_name} ejecutada exitosamente")
            
            # Extraer contenido del resultado
            if result.content:
                # El resultado puede tener múltiples partes (text, image, etc.)
                contents = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        contents.append(content.text)
                    elif hasattr(content, 'data'):
                        contents.append(content.data)
                
                return {"result": contents[0] if len(contents) == 1 else contents}
            
            return {"result": None}
            
        except Exception as e:
            self.logger.error(
                f"Error ejecutando herramienta {tool_name}: {str(e)}"
            )
            return {"error": f"Error ejecutando herramienta {tool_name}: {str(e)}"}
    
    async def close(self) -> None:
        """
        Cierra la conexión con el servidor MCP y libera recursos.
        """
        self.logger.info(f"Cerrando conexión con servidor MCP: {self.server_name}")
        await self._cleanup()
        self._tools = None
        self._tools_map = {}
        self._langchain_tools = None
        self.logger.info(f"Conexión cerrada exitosamente para: {self.server_name}")
    
    def get_server_name(self) -> str:
        """Retorna el nombre del servidor MCP."""
        return self.server_name
    
    def get_transport_type(self) -> str:
        """Retorna el tipo de transporte."""
        return "streamable_http"
    
    async def _aenter_(self) -> "MCPClientAdapter":
        """Soporte para uso como context manager async."""
        await self._initialize_client()
        return self
    
    async def _aexit_(self, exc_type, exc_val, exc_tb) -> None:
        """Cierra recursos al salir del context manager."""
        await self.close()