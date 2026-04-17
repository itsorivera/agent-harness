from typing import Dict, Optional, List
from langchain_core.tools import tool, BaseTool
from langchain_core.runnables.config import RunnableConfig
from src.core.ports.long_term_memory_port import LongTermMemoryPort, MemoryEntity, MemoryType
from src.core.ports.embedder_provider_port import EmbeddingProviderPort
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_USER_ID = "system"

def get_memory_tools(ltm_port: LongTermMemoryPort, embedder: EmbeddingProviderPort) -> List[BaseTool]:
    """
    Factory that returns tools with injected LTM repository and embedding provider.
    This pattern breaks circular dependencies between the DI container and the tools.
    """

    @tool
    async def store_memory_tool(
        content: str,
        memory_type: MemoryType,
        metadata: Optional[Dict[str, str]] = None,
        config: Optional[RunnableConfig] = None,
    ) -> str:
        """
        Store a long-term memory in the system.
        Use this tool to save important information about user preferences,
        experiences, or general knowledge that might be useful in future interactions.
        """
        config = config or RunnableConfig()
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id", SYSTEM_USER_ID)
        thread_id = configurable.get("thread_id")

        try:
            # 1. Generar embedding (Inyectado vía closure)
            embedding = embedder.embed_query(content)
            
            # 2. Verificar duplicados
            is_duplicate = await ltm_port.check_duplicate(
                embedding=embedding,
                user_id=user_id,
                distance_threshold=0.05
            )
            
            if is_duplicate:
                return "A similar memory already exists. Skipping storage to avoid redundancy."

            # 3. Crear entidad y guardar
            memory = MemoryEntity(
                content=content,
                memory_type=memory_type,
                user_id=user_id,
                metadata=metadata,
                thread_id=thread_id
            )
            
            success = await ltm_port.store_memory(memory, embedding)
            return f"Successfully stored {memory_type.value} memory: {content}" if success else "Failed to store memory."
                
        except Exception as e:
            logger.error(f"Error in store_memory_tool: {str(e)}")
            return f"Error storing memory: {str(e)}"


    @tool
    async def retrieve_memories_tool(
        query: str,
        memory_type: Optional[List[MemoryType]] = None,
        limit: int = 5,
        config: Optional[RunnableConfig] = None,
    ) -> str:
        """
        Retrieve long-term memories relevant to the query.
        Use this tool to access previously stored information about user
        preferences, experiences, or general knowledge.
        """
        config = config or RunnableConfig()
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id", SYSTEM_USER_ID)

        try:
            # 1. Generar embedding de la consulta (Inyectado vía closure)
            query_embedding = embedder.embed_query(query)
            
            # 2. Recuperar del repositorio
            m_type = memory_type[0] if memory_type and len(memory_type) > 0 else None
            
            stored_memories = await ltm_port.retrieve_memories(
                query_embedding=query_embedding,
                user_id=user_id,
                memory_type=m_type,
                limit=limit,
                distance_threshold=0.35
            )

            if not stored_memories:
                return "No relevant long-term memories found for this query."
                
            response = ["Long-term memories retrieved:"]
            for memory in stored_memories:
                response.append(f"- [{memory.memory_type.value}] {memory.content}")

            return "\n".join(response)

        except Exception as e:
            logger.error(f"Error in retrieve_memories_tool: {str(e)}")
            return f"Error retrieving memories: {str(e)}"

    return [store_memory_tool, retrieve_memories_tool]