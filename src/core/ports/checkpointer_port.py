"""
Puerto de salida para Checkpointer (Hexagonal Architecture)

Define la interfaz que debe implementar cualquier adaptador de checkpoint
para persistir el estado de las conversaciones.
"""
from abc import ABC, abstractmethod
from typing import Any


class CheckpointerPort(ABC):
    """
    Puerto abstracto para implementaciones de checkpoint.
    
    Define el contrato que deben cumplir los adaptadores de checkpoint
    (e.g., PostgreSQL, Redis, MongoDB, etc.)
    """
    
    @abstractmethod
    async def get_checkpointer(self) -> Any:
        """
        Obtiene un checkpointer configurado (versión asíncrona).
        
        Returns:
            Un objeto checkpointer configurado y listo para usar
            
        Ejemplo:
            checkpointer = await adapter.get_checkpointer()
            # usar checkpointer
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        Limpia recursos y conexiones del checkpointer.
        
        Este método debe ser llamado cuando ya no se necesite
        el checkpointer para liberar recursos apropiadamente.
        """
        pass


class CheckpointerPortSync(ABC):
    """
    Puerto abstracto para implementaciones de checkpoint síncronas.
    
    Define el contrato que deben cumplir los adaptadores de checkpoint
    en modo síncrono.
    """
    
    @abstractmethod
    def get_checkpointer(self) -> Any:
        """
        Obtiene un checkpointer configurado (versión síncrona).
        
        Returns:
            Un objeto checkpointer configurado y listo para usar
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Limpia recursos y conexiones del checkpointer.
        
        Este método debe ser llamado cuando ya no se necesite
        el checkpointer para liberar recursos apropiadamente.
        """
        pass