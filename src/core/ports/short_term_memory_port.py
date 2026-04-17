"""
Puerto de salida para Short Term Memory (STM) - Hexagonal Architecture

Define la interfaz que debe implementar cualquier adaptador de memoria a corto plazo
para persistir el estado de las conversaciones.
"""
from abc import ABC, abstractmethod
from typing import Any


class ShortTermMemoryPort(ABC):
    """
    Puerto abstracto para implementaciones de memoria a corto plazo.
    
    Define el contrato que deben cumplir los adaptadores de STM
    (e.g., PostgreSQL, Redis, MongoDB, etc.)
    """
    
    @abstractmethod
    async def get_state_manager(self) -> Any:
        """
        Obtiene el gestor de estado (checkpointer) configurado (versión asíncrona).
        
        Returns:
            Un objeto de gestión de estado listo para usar.
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        Limpia recursos y conexiones de la memoria.
        """
        pass


class ShortTermMemoryPortSync(ABC):
    """
    Puerto abstracto para implementaciones de memoria a corto plazo síncronas.
    """
    
    @abstractmethod
    def get_state_manager(self) -> Any:
        """
        Obtiene el gestor de estado configurado (versión síncrona).
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Limpia recursos y conexiones de la memoria.
        """
        pass