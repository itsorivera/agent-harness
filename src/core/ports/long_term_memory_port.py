from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"

class MemoryEntity:
    def __init__(
        self, 
        content: str, 
        memory_type: MemoryType, 
        user_id: str, 
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None,
        memory_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ):
        self.content = content
        self.memory_type = memory_type
        self.user_id = user_id
        self.metadata = metadata or {}
        self.created_at = created_at
        self.memory_id = memory_id
        self.thread_id = thread_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "memory_type": self.memory_type.value,
            "user_id": self.user_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "memory_id": self.memory_id,
            "thread_id": self.thread_id
        }

class LongTermMemoryPort(ABC):
    """
    Port (Interface) for Long Term Memory Persistence.
    Following SOLID: Interface Segregation and Dependency Inversion.
    """

    @abstractmethod
    async def store_memory(self, memory: MemoryEntity, embedding: List[float]) -> bool:
        """Stores a memory with its vector embedding."""
        pass

    @abstractmethod
    async def retrieve_memories(
        self, 
        query_embedding: List[float], 
        user_id: str, 
        memory_type: Optional[MemoryType] = None,
        limit: int = 5,
        distance_threshold: float = 0.1
    ) -> List[MemoryEntity]:
        """Retrieves top-k relevant memories using vector similarity search."""
        pass

    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """Deletes a single memory by its ID."""
        pass

    @abstractmethod
    async def check_duplicate(
        self, 
        embedding: List[float], 
        user_id: str, 
        distance_threshold: float = 0.05
    ) -> bool:
        """Checks if a similar memory already exists to avoid redundant information."""
        pass
