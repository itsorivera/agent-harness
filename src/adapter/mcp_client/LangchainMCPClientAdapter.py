from typing import Dict, Any, List, Optional
import logging
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.core.ports.mcp_client_port import MCPClientPort

class LangchainMCPClientAdapter(MCPClientPort):
    """
    Adaptador MCP usando LangChain MCP Adapters con transporte HTTP.
    """
    TRANSPORT_TYPE = "streamable_http"
    
    def _init_(self, server_url: str, server_name: str = "default"):
        """
        Inicializa el adaptador LangChain MCP.
        
        Args:
            server_url: URL del servidor MCP (debe soportar HTTP streamable)
            server_name: Nombre identificador para logging y referencia
        """
        self.server_url = server_url
        self.server_name = server_name
        self._client: Optional[MultiServerMCPClient] = None
        self._tools: Optional[List[Any]] = None
        self.logger = logging.getLogger(f"{__name__}.LangchainLangchainMCPClientAdapter")
    
    async def _initialize_client(self) -> None:
        """
        Inicializa el MultiServerMCPClient si no está inicializado.
        
        Realiza lazy initialization del cliente para evitar
        conexiones innecesarias al instanciar el adaptador.
        
        Raises:
            ValueError: Si no se proporciona URL válida
            ConnectionError: Si no se puede conectar al servidor
        """
        if self._client is None:
            servers = {
                self.server_name: {
                    "url": self.server_url,
                    "transport": "streamable_http",
                }
            }
            
            servers = {k: v for k, v in servers.items() if v["url"]}
            
            if not servers:
                raise ValueError(
                    f"No se proporcionó URL válida para servidor MCP {self.server_name}"
                )
            
            try:
                self.logger.info(
                    f"Inicializando MCP client para servidor: {self.server_name} "
                    f"con URL: {self.server_url}"
                )
                self._client = MultiServerMCPClient(servers)
                
                self.logger.info(
                    f"Obteniendo herramientas del servidor MCP: {self.server_name}"
                )
                self._tools = await self._client.get_tools()
                self.logger.info(
                    f"Cargadas {len(self._tools)} herramientas desde "
                    f"servidor MCP: {self.server_name}"
                )
            except Exception as e:
                import traceback
                self.logger.error(
                    f"Error al inicializar MCP client para {self.server_name}: {str(e)}"
                )
                self.logger.error(traceback.format_exc())
                self._tools = []
                raise ConnectionError(
                    f"No se pudo conectar al servidor MCP {self.server_name}: {str(e)}"
                ) from e
    
    async def get_tools(self) -> List[Any]:
        """
        Obtiene las herramientas disponibles desde el servidor MCP.
        
        Returns:
            Lista de herramientas compatibles con LangChain
        """
        try:
            if self._tools is None:
                await self._initialize_client()
            
            return list(self._tools) if self._tools else []
        except Exception as e:
            self.logger.error(
                f"Error obteniendo herramientas del servidor MCP "
                f"{self.server_name}: {str(e)}"
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
            if self._tools is None:
                await self._initialize_client()
            
            if not self._tools:
                self.logger.warning(
                    f"No hay herramientas disponibles para servidor MCP "
                    f"{self.server_name}"
                )
                return {
                    "error": f"No hay herramientas disponibles para "
                             f"servidor MCP {self.server_name}"
                }
            
            for tool in self._tools:
                if tool.name == tool_name:
                    self.logger.info(
                        f"Ejecutando herramienta {tool_name} en servidor MCP "
                        f"{self.server_name}"
                    )
                    try:
                        result = await tool.ainvoke(tool_input)
                        self.logger.info(
                            f"Herramienta {tool_name} ejecutada exitosamente"
                        )
                        return {"result": result}
                    except Exception as tool_error:
                        self.logger.error(
                            f"Error ejecutando herramienta {tool_name}: "
                            f"{str(tool_error)}"
                        )
                        return {
                            "error": f"Error ejecutando herramienta "
                                     f"{tool_name}: {str(tool_error)}"
                        }
            
            self.logger.warning(
                f"Herramienta {tool_name} no encontrada en servidor MCP "
                f"{self.server_name}"
            )
            return {
                "error": f"Herramienta {tool_name} no encontrada en "
                         f"servidor MCP {self.server_name}"
            }
        except Exception as e:
            self.logger.error(
                f"Error en execute_tool para {self.server_name}: {str(e)}"
            )
            return {"error": f"Error ejecutando herramienta {tool_name}: {str(e)}"}
    
    async def close(self) -> None:
        """
        Cierra la conexión con el servidor MCP y libera recursos.
        """
        if self._client:
            try:
                self.logger.info(
                    f"Cerrando conexión con servidor MCP: {self.server_name}"
                )
                # MultiServerMCPClient no tiene método close explícito,
                # pero limpiamos las referencias
                self._client = None
                self._tools = None
                self.logger.info(
                    f"Conexión cerrada exitosamente para: {self.server_name}"
                )
            except Exception as e:
                self.logger.error(
                    f"Error al cerrar conexión MCP {self.server_name}: {str(e)}"
                )
    
    def get_server_name(self) -> str:
        """Retorna el nombre del servidor MCP."""
        return self.server_name
    
    def get_transport_type(self) -> str:
        """Retorna el tipo de transporte (HTTP streamable)."""
        return self.TRANSPORT_TYPE
    
    async def _aenter_(self) -> "LangchainMCPClientAdapter":
        """Soporte para uso como context manager async."""
        await self._initialize_client()
        return self
    
    async def _aexit_(self, exc_type, exc_val, exc_tb) -> None:
        """Cierra recursos al salir del context manager."""
        await self.close()