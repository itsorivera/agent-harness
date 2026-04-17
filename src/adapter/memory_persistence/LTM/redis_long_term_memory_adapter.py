import os
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import ulid
import json

from redisvl.index import AsyncSearchIndex
from redisvl.query import VectorRangeQuery, VectorQuery
from redisvl.query.filter import Tag

from src.core.ports.long_term_memory_port import LongTermMemoryPort, MemoryEntity, MemoryType
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RedisLongTermMemoryAdapter(LongTermMemoryPort):
    """
    Adapter that implements the LongTermMemoryPort using RedisVL.
    """

    def __init__(self, index: AsyncSearchIndex):
        self._index = index

    async def store_memory(self, memory: MemoryEntity, embedding: List[float]) -> bool:
        """
        Converts the memory entity to the expected RedisJSON format and persists it.
        """
        logger.info(f"Storing memory for user {memory.user_id} in Redis.")
        
        # Generation of data for RedisJSON storage
        memory_data = {
            "user_id": str(memory.user_id),
            "content": memory.content,
            "memory_type": str(memory.memory_type.value),
            "metadata": json.dumps(memory.metadata),
            "created_at": datetime.now().isoformat(),
            "embedding": embedding,
            "memory_id": str(ulid.ULID()),
            "thread_id": memory.thread_id,
        }

        try:
            # Use load to insert into the existing index
            await self._index.load([memory_data])
            logger.info(f"Memory stored correctly with ID: {memory_data['memory_id']}")
            return True
        except Exception as e:
            logger.error(f"Error storing memory in Redis: {e}")
            return False

    async def retrieve_memories(
        self, 
        query_embedding: List[float], 
        user_id: str, 
        memory_type: Optional[MemoryType] = None,
        limit: int = 5,
        distance_threshold: float = 0.1
    ) -> List[MemoryEntity]:
        """
        Performs a semantic search on Redis restricted to the user.
        """
        logger.debug(f"Retrieving memories for user {user_id} with threshold {distance_threshold}")
        
        # Build Vector Range Query with filters
        vector_query = VectorRangeQuery(
            vector=query_embedding,
            vector_field_name="embedding",
            num_results=limit,
            distance_threshold=distance_threshold,
            return_fields=["content", "memory_type", "metadata", "created_at", "memory_id", "user_id", "thread_id"]
        )

        filter_expr = Tag("user_id") == user_id
        if memory_type:
            filter_expr &= Tag("memory_type") == str(memory_type.value)
        
        vector_query.set_filter(filter_expr)

        try:
            results = await self._index.query(vector_query)
            
            memories = []
            for doc in results:
                # Map from Redis result to Domain Entity
                memories.append(MemoryEntity(
                    content=doc["content"],
                    memory_type=MemoryType(doc["memory_type"]),
                    user_id=doc["user_id"],
                    metadata=json.loads(doc.get("metadata", "{}")),
                    created_at=doc["created_at"],
                    memory_id=doc["memory_id"],
                    thread_id=doc.get("thread_id")
                ))
            
            return memories
        except Exception as e:
            logger.error(f"Error querying memories in Redis: {e}")
            return []

    async def check_duplicate(
        self, 
        embedding: List[float], 
        user_id: str, 
        distance_threshold: float = 0.05
    ) -> bool:
        """
        Check for very similar memories to prevent redundant extraction.
        """
        results = await self.retrieve_memories(
            query_embedding=embedding,
            user_id=user_id,
            limit=1,
            distance_threshold=distance_threshold
        )
        return len(results) > 0

    async def delete_memory(self, memory_id: str) -> bool:
        query = VectorQuery(
            vector=[0] * 1536, 
            filter_expression=(Tag("memory_id") == memory_id),
            num_results=1,
            return_fields=["id"]
        )
        
        try:
            results = await self._index.query(query)
            if results:
                await self._index._redis.delete(results[0]["id"])
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return False
