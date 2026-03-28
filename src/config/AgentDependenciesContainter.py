from typing import Optional, Dict
from functools import lru_cache
from fastapi import Depends
from src.core.tools import FINANCIAL_ADVISOR_TOOLS
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

logger = get_logger(__name__)

class AgentDependencies:
    
    def __init__(self):
        self._checkpointer_adapter: Optional[PostgresCheckpointerAdapterAsync] = None
        self._llm_adapters_cache: Dict[str, LLMProviderPort] = {}
        self._channel_mcp_client: Optional[MCPClientPort] = None
        self._block_card_mcp_client: Optional[MCPClientPort] = None
        self._security_mcp_client: Optional[MCPClientPort] = None
        self._general_agent: Optional[AgentPort] = None
    
    @property
    def checkpointer_adapter(self) -> PostgresCheckpointerAdapterAsync:
        """Lazy loading del checkpointer"""
        if self._checkpointer_adapter is None:
            logger.info("Inicializando PostgresCheckpointerAdapter")
            self._checkpointer_adapter = PostgresCheckpointerAdapterAsync()
        return self._checkpointer_adapter
    
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
            logger.info("Inicializando agente general...")
            
            llm_adapter = self.get_llm_adapter()
            checkpointer = self.checkpointer_adapter
            graph_strategy = ReActGraphStrategy()
            
            agent_adapter = LanggraphAgentAdapter(
                agent_name="GeneralAgent",
                llm_port=llm_adapter,
                model_id=resolve_model_id(),
                system_prompt=GENERAL_AGENT_PROMPT.render(
                    **GENERAL_AGENT_PERSONALITY.model_dump()
                ),
                checkpointer_port=checkpointer,
                tools=[],
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