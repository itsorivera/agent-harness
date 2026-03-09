"""
Puerto para la creación y gestión de agentes.

Define el contrato que deben implementar todos los agentes del sistema,
permitiendo crear diferentes tipos de agentes (ChannelAgent, BlockCardAgent, etc.)
siguiendo el patrón de arquitectura hexagonal.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class AgentPort(ABC):
    """
    Puerto abstracto para agentes del sistema.
    
    Define las operaciones básicas que todo agente debe implementar:
    - Creación/inicialización del agente
    - Procesamiento de mensajes
    - Limpieza de recursos
    """

    @abstractmethod
    async def create_agent(self) -> Any:
        """
        Crea e inicializa el agente con su grafo compilado.
        
        Returns:
            Any: El grafo compilado del agente listo para ejecutar
            
        Raises:
            RuntimeError: Si hay un error durante la inicialización
        """
        pass

    @abstractmethod
    async def process_message(self, message: str, thread_id: str) -> Dict[str, Any]:
        """
        Procesa un mensaje utilizando el agente.
        
        Args:
            message: El mensaje de entrada a procesar
            thread_id: Identificador único del hilo de conversación
            
        Returns:
            Dict[str, Any]: Resultado del procesamiento incluyendo mensajes generados
            
        Raises:
            RuntimeError: Si el agente no ha sido inicializado
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Limpia los recursos utilizados por el agente.
        
        Debe liberar:
        - Conexiones a bases de datos (checkpointer)
        - Recursos del proveedor de LLM
        - Clientes MCP u otros servicios externos
        """
        pass