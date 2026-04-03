from typing import Optional, Dict
from functools import lru_cache
from fastapi import Depends
from src.core.tools import FINANCIAL_ADVISOR_TOOLS
from src.core.local_tools import MEMORY_TOOLS
from src.adapter.repository.memory_persistence.PostgresCheckpointerAdapter import PostgresCheckpointerAdapterAsync
from src.adapter.repository.llm_provider.AWSBedrockLLMProviderAdapter import AWSLLMProviderAdapter
from src.adapter.repository.llm_provider.IAFoundryProviderLLMAdapter import IAFoundryLLMAdapter
from src.core.ports.mcp_client_port import MCPClientPort
from src.core.ports.llm_provider_port import LLMProviderPort
from src.adapter.repository.agent.LanggraphAgentAdapter import LanggraphAgentAdapter
from src.core.langgraph.graph_strategies.ReActGraphStrategy import ReActGraphStrategy
from src.core.ports.agent_port import AgentPort
from src.core.prompts import GENERAL_AGENT_PROMPT, FINANCIAL_ADVISOR_SYSTEM_PROMPT
from src.config.app_config import config
from src.config.agent_personalities import GENERAL_AGENT_PERSONALITY
from src.utils.logger import get_logger, set_correlation_id
from src.utils.ConfigResolver import resolve_model_id, resolve_llm_provider
from datetime import datetime
import os
from redis.asyncio import Redis
from redisvl.index import AsyncSearchIndex
from redisvl.schema.schema import IndexSchema
from src.core.ports.ltm_repository_port import LTMRepositoryPort
from src.adapter.repository.memory_persistence.LTM.RedisLTMRepositoryAdapter import RedisLTMRepositoryAdapter
from src.core.ports.embedder_provider_port import EmbeddingProviderPort
from src.adapter.repository.embedder_provider.AWSBedrockEmbeddingAdapter import AWSBedrockEmbeddingAdapter

logger = get_logger(__name__)

class AgentDependencies:
    
    def __init__(self):
        self._checkpointer_adapter: Optional[PostgresCheckpointerAdapterAsync] = None
        self._llm_adapters_cache: Dict[str, LLMProviderPort] = {}
        self._channel_mcp_client: Optional[MCPClientPort] = None
        self._block_card_mcp_client: Optional[MCPClientPort] = None
        self._security_mcp_client: Optional[MCPClientPort] = None
        self._general_agent: Optional[AgentPort] = None
        self._ltm_repository: Optional[LTMRepositoryPort] = None
        self._redis_client: Optional[Redis] = None
        self._redis_index: Optional[AsyncSearchIndex] = None
        self._embedding_adapter: Optional[EmbeddingProviderPort] = None
    
    @property
    def checkpointer_adapter(self) -> PostgresCheckpointerAdapterAsync:
        """Lazy loading del checkpointer"""
        if self._checkpointer_adapter is None:
            logger.info("Inicializando PostgresCheckpointerAdapter")
            self._checkpointer_adapter = PostgresCheckpointerAdapterAsync()
        return self._checkpointer_adapter
    
    @property
    def redis_client(self) -> Redis:
        """Lazy loading of Redis client"""
        if self._redis_client is None:
            redis_url = f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}"
            logger.info(f"Connecting to Redis at {redis_url}")
            self._redis_client = Redis.from_url(redis_url)
        return self._redis_client

    async def get_ltm_index(self) -> AsyncSearchIndex:
        """Lazy loading and initialization of RedisVL search index"""
        if self._redis_index is None:
            logger.info("Initializing RedisVL Long Term Memory Index")
            # Load schema from YAML (the one we created in db/memory)
            # Find the path relative to the root/package
            schema_path = os.path.join(os.getcwd(), "db", "memory", "redis_ltm_schema.yaml")
            schema = IndexSchema.from_yaml(schema_path)
            
            self._redis_index = AsyncSearchIndex(
                schema=schema,
                redis_client=self.redis_client
            )
            # Ensure index exists (idempotent, omg)
            if not await self._redis_index.exists():
                logger.info(f"Creating new Redis index: {schema.index.name}")
                await self._redis_index.create()
                
        return self._redis_index

    async def get_ltm_repository(self) -> LTMRepositoryPort:
        """Lazy loading of LTM Repository adapter"""
        if self._ltm_repository is None:
            index = await self.get_ltm_index()
            logger.info("Initializing RedisLTMRepositoryAdapter")
            self._ltm_repository = RedisLTMRepositoryAdapter(index=index)
        return self._ltm_repository
    
    @property
    def embedding_adapter(self) -> EmbeddingProviderPort:
        """Lazy loading of Embedding provider"""
        if self._embedding_adapter is None:
            logger.info("Initializing AWSBedrockEmbeddingAdapter")
            self._embedding_adapter = AWSBedrockEmbeddingAdapter(
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                region_name=config.AWS_REGION
            )
        return self._embedding_adapter
    
    SUPPORTED_LLM_PROVIDERS = {
        "aws_bedrock": AWSLLMProviderAdapter,
        "ia_foundry": IAFoundryLLMAdapter,
    }
        
    def get_llm_adapter(self, provider: Optional[str] = None) -> LLMProviderPort:
        """
        Obtiene o crea un adapter de LLM para el provider especificado.
        """
        provider = resolve_llm_provider(provider)
        
        # Check cache
        if provider in self._llm_adapters_cache:
            logger.debug(f"Retornando LLM adapter cacheado para: {provider}")
            return self._llm_adapters_cache[provider]
        
        # Create adapter
        adapter_class = self.SUPPORTED_LLM_PROVIDERS[provider]
        logger.info(f"Inicializando LLM adapter: {provider} ({adapter_class.__name__})")
        
        adapter = adapter_class()
        
        # Save to cache
        self._llm_adapters_cache[provider] = adapter
        logger.info(f"LLM adapter '{provider}' creado y cacheado: {adapter.get_provider_name()}")
        
        return adapter

    async def get_general_agent(self) -> AgentPort:
        """
        Obtiene o crea el agente general, asegurando que esté inicializado.
        """
        if self._general_agent is None:
            logger.info("Initializing general agent...")
            
            llm_adapter = self.get_llm_adapter()
            checkpointer = self.checkpointer_adapter
            ltm_repo = await self.get_ltm_repository()
            embedder = self.embedding_adapter
            
            # Use factory to break circular dependency
            memory_tools = get_memory_tools(ltm_repo, embedder)
            
            graph_strategy = ReActGraphStrategy()
            
            agent_adapter = LanggraphAgentAdapter(
                agent_name="GeneralAgent",
                llm_port=llm_adapter,
                model_id=resolve_model_id(),
                system_prompt=GENERAL_AGENT_PROMPT.render(
                    **GENERAL_AGENT_PERSONALITY.model_dump()
                ),
                checkpointer_port=checkpointer,
                tools=memory_tools,
                graph_strategy=graph_strategy,
            )
            
            await agent_adapter.create_agent()
            self._general_agent = agent_adapter
            
        return self._general_agent
    
    async def get_financial_advisor_agent(self) -> AgentPort:
        """
        Crea un agente especializado en asesoría financiera, con herramientas específicas.
        """
        logger.info("Inicializando agente de asesoría financiera...")
        
        llm_adapter = self.get_llm_adapter()
        checkpointer = self.checkpointer_adapter
        graph_strategy = ReActGraphStrategy()
        
        # Injection of HITL configuration
        hitl_config = {
            "place_order": {"allowed_decisions": ["approve", "edit", "reject"]},
            # "transfer_funds": {"allowed_decisions": ["approve", "reject"]},
            # "delete_record": {"allowed_decisions": ["approve"]} # Only approve or nothing
        }

        agent_adapter = LanggraphAgentAdapter(
            agent_name="FinancialAdvisorAgent",
            llm_port=llm_adapter,
            model_id=resolve_model_id(),
            system_prompt=FINANCIAL_ADVISOR_SYSTEM_PROMPT.render(
                **GENERAL_AGENT_PERSONALITY.model_dump()
            ),
            checkpointer_port=checkpointer,
            tools=FINANCIAL_ADVISOR_TOOLS,
            graph_strategy=graph_strategy,
            hitl_config=hitl_config
        )

        
        await agent_adapter.create_agent()
        return agent_adapter

@lru_cache()
def get_agent_dependencies() -> AgentDependencies:
    return AgentDependencies()

async def get_agent_general() -> AgentPort:
    dependencies = get_agent_dependencies()
    return await dependencies.get_general_agent()

async def get_financial_advisor_agent() -> AgentPort:
    dependencies = get_agent_dependencies()
    return await dependencies.get_financial_advisor_agent()