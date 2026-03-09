from abc import ABC, abstractmethod
from typing import Any, Dict, List


class MCPClientPort(ABC):
    """
    Puerto abstracto para implementaciones de clientes MCP.
    
    Define el contrato que deben cumplir los adaptadores de MCP
    (e.g., LangChain MCP Adapters, Google ADK MCPToolset, etc.)
    """
    
    @abstractmethod
    async def get_tools(self) -> List[Any]:
        """
        Obtiene las herramientas disponibles desde el servidor MCP.
        
        Returns:
            Lista de herramientas compatibles con el framework de agentes
            
        Raises:
            ConnectionError: Si no se puede conectar al servidor MCP
            RuntimeError: Si hay errores al cargar las herramientas
        """
        pass
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta una herramienta específica en el servidor MCP.
        
        Args:
            tool_name: Nombre de la herramienta a ejecutar
            tool_input: Parámetros de entrada para la herramienta
            
        Returns:
            Diccionario con el resultado de la ejecución o error
            
        Raises:
            ValueError: Si la herramienta no existe
            RuntimeError: Si hay errores durante la ejecución
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Cierra la conexión con el servidor MCP y libera recursos.
        
        Este método debe ser llamado cuando ya no se necesite
        el cliente para liberar recursos apropiadamente
        (conexiones, sesiones, etc.)
        """
        pass
    
    @abstractmethod
    def get_server_name(self) -> str:
        """
        Retorna el nombre identificador del servidor MCP.
        
        Returns:
            Nombre del servidor MCP configurado
        """
        pass
    
    @abstractmethod
    def get_transport_type(self) -> str:
        """
        Retorna el tipo de transporte utilizado.
        
        Returns:
            Tipo de transporte (e.g., "streamable_http", "sse", "stdio")
        """
        pass