from typing import Any, Dict, List, Optional
from langchain_core.tools import BaseTool
from src.core.ports.agent_port import AgentPort
from src.core.ports.short_term_memory_port import ShortTermMemoryPortSync, ShortTermMemoryPort
from src.core.ports.llm_provider_port import LLMProviderPort
from .nodes import NodeFunctions
from .states import AgentState
from src.utils.logger import get_logger
from src.utils.observability.metrics import track_latency
from .graph_strategy_port import GraphStrategyPort


class LanggraphAgentAdapter(AgentPort):
    def __init__(
            self,
            agent_name: str,
            llm_port: LLMProviderPort,
            model_id: str,
            system_prompt: str,
            checkpointer_port: ShortTermMemoryPort | ShortTermMemoryPortSync,
            tools: List[BaseTool],
            graph_strategy: Optional[GraphStrategyPort] = None,
            hitl_config: Optional[Dict[str, Any]] = None,
    ): 
        """
        Inicializa el adaptador de agente langgraph.
        
        Args:
            agent_name: Nombre del agente
            llm_port: Puerto para acceso a modelos de lenguaje
            model_id: Identificador del modelo LLM a usar (ej: "anthropic.claude-3-sonnet-20240229-v1:0",
                     "amazon.nova-pro-v1:0", "mistral.mixtral-8x7b-instruct-v0:1")
            system_prompt: Prompt del sistema
            checkpointer_port: Puerto para persistencia de estado
            tools: Lista de herramientas ya resueltas para el agente (inyectadas, no fetcheadas)
            graph_strategy: Estrategia para construir el grafo del agente
            hitl_config: Configuración para human-in-the-loop
        """
        self.agent_name = agent_name
        self.llm_port = llm_port
        self.model_id = model_id
        self.system_prompt = system_prompt
        self.checkpointer_port = checkpointer_port
        self.tools = tools
        self.agent_graph_compiled = None
        self.graph_strategy = graph_strategy
        self.hitl_config = hitl_config or {}
        self.logger = get_logger(f"{__name__}.{self.agent_name}")

    
    async def create_agent(self) -> Any:
        """
        Crea el agente langgraph con su grafo compilado.
        
        Las tools ya vienen inyectadas en el constructor, siguiendo el principio
        de inversión de dependencias. Este método solo se encarga de:
        1. Configurar el LLM
        2. Crear las funciones de nodos
        3. Construir y compilar el grafo
        """
        self.logger.info(f"Iniciando creación del agente {self.agent_name}")
        
        # Imprimir nombres de las herramientas inyectadas
        tool_names = [tool.name for tool in self.tools]
        self.logger.info(f"Herramientas disponibles para {self.agent_name}: ({len(self.tools)}) >> {tool_names}")
        
        # Configurar LLM con el model_id inyectado
        llm = self.llm_port.get_llm(self.model_id)
        self.logger.info(f"LLM configurado: {self.model_id} para {self.agent_name}")
        
        models = {"conversation_llm": llm}
        
        # Crear funciones de nodos
        self.logger.info(f"Creando funciones de nodos para {self.agent_name}...")
        node_funcs = NodeFunctions(
            models, 
            system_prompt=self.system_prompt, 
            tools=self.tools,
            hitl_config=self.hitl_config
        )

        node_functions = {
            "call_model": node_funcs.call_model,
            "hitl_gate": node_funcs.hitl_gate,
            "tool_node": node_funcs.tool_node,
            "should_continue": node_funcs.should_continue
        }
        
        # Construir grafo (reutilizamos el builder, en producción podrías crear uno específico)
        self.logger.info(f"Construyendo grafo del agente {self.agent_name}...")
        #agent_graph = build_react_agent_graph(
        #    state_schema=AgentState,
        #    node_functions=node_functions,
        #)
        agent_graph = self.graph_strategy.build_graph(
            state_schema=AgentState,
            node_functions=node_functions,
        )
        
        self.logger.info("Compilando grafo con memoria a corto plazo...")
        checkpointer = await self.checkpointer_port.get_state_manager()
        self.agent_graph_compiled = agent_graph.compile(checkpointer=checkpointer)
        
        self.logger.info(f"Agente {self.agent_name} creado exitosamente")
        return self.agent_graph_compiled

    @track_latency("agent_process_message")
    async def process_message(
        self, 
        message: Optional[str] = None, 
        thread_id: str = "default",
        user_id: Optional[str] = None,
        decisions: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje con el agente o reanuda si hay decisiones de HITL.
        
        Args:
            message: Consulta o comando del usuario (Opcional si es reanudación)
            thread_id: ID del hilo de conversación para mantener contexto
            user_id: ID del usuario
            decisions: Decisiones de supervisión humana (HITL)
            
        Returns:
            Diccionario con los mensajes y el resultado del procesamiento
        """
        from langgraph.types import Command

        if not self.agent_graph_compiled:
            raise RuntimeError("El agente no ha sido inicializado. Llama a create_agent() primero.")
        
        self.logger.info(f"Petición para agente {self.agent_name} en thread {thread_id}")
        
        config = {"configurable": {
            "thread_id": thread_id,
            "user_id": user_id or "system"
            }}

        # Logic to determine input (new message vs HITL resumption)
        if decisions:
            self.logger.info(f"Reanudando hilo {thread_id} con decisiones HITL")
            # Convertimos modelos Pydantic a dicts si es necesario para evitar AttributeError en nodos.py
            decisions_data = [d.model_dump() if hasattr(d, "model_dump") else d for d in decisions]
            input_data = Command(resume={"decisions": decisions_data})

        else:
            self.logger.info(f"Iniciando nuevo procesamiento en hilo {thread_id}")
            input_data = {"messages_tools": message}

        result = await self.agent_graph_compiled.ainvoke(input_data, config)

        final_msg = result['messages'][-1].content if hasattr(result['messages'][-1], 'content') else str(result['messages'][-1])
        # Sanitizamos el log para evitar errores en Windows con emojis
        safe_final_msg = final_msg.encode("ascii", "ignore").decode("ascii")
        self.logger.debug(f"Respuesta final generada de agente {self.agent_name}: {safe_final_msg}")

        return result

    @track_latency("agent_stream_message")
    async def stream_message(
        self, 
        message: Optional[str] = None, 
        thread_id: str = "default",
        user_id: Optional[str] = None,
        decisions: Optional[List[Any]] = None
    ):
        """
        Procesa un mensaje en modo streaming utilizando astream de LangGraph.
        Yields chunks de la respuesta a medida que se generan.
        """
        from langgraph.types import Command
        import json

        if not self.agent_graph_compiled:
            raise RuntimeError("El agente no ha sido inicializado. Llama a create_agent() primero.")
        
        self.logger.info(f"Petición STREAM para agente {self.agent_name} en thread {thread_id}")
        
        config = {"configurable": {
            "thread_id": thread_id,
            "user_id": user_id or "system"
            }}

        if decisions:
            decisions_data = [d.model_dump() if hasattr(d, "model_dump") else d for d in decisions]
            input_data = Command(resume={"decisions": decisions_data})
        else:
            input_data = {"messages_tools": message}

        # Utilizamos astream con stream_mode="messages" para obtener tokens individuales
        # de los mensajes que se van generando en el grafo.
        async for chunk, metadata in self.agent_graph_compiled.astream(
            input_data, 
            config, 
            stream_mode="messages"
        ):
            if hasattr(chunk, "content") and chunk.content:
                content = chunk.content
                
                # Caso 1: Es una lista (común en modelos de Bedrock)
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict):
                            # Extraemos texto de bloques tipo dict {'type': 'text', 'text': '...'}
                            text = block.get("text", "")
                            if text: 
                                yield f"data: {text}\n\n"
                        elif isinstance(block, str):
                            yield f"data: {block}\n\n"
                
                # Caso 2: Es un string directo (Tokens normales)
                elif isinstance(content, str):
                    yield f"data: {content}\n\n"
                
                # Caso 3: Fallback para cualquier otro tipo de contenido
                else:
                    if content is not None:
                        yield f"data: {str(content)}\n\n"

    
    async def cleanup(self) -> None:
        """
        Limpia los recursos del agente.
        """
        self.logger.info(f"Limpiando recursos del agente {self.agent_name}...")
        
        try:
            await self.checkpointer_port.cleanup()
            self.logger.info("Memoria STM limpiada")
        except Exception as e:
            self.logger.error(f"Error al limpiar memoria STM: {e}")
        
        try:
            self.llm_port.cleanup()
            self.logger.info("LLM provider limpiado")
        except Exception as e:
            self.logger.error(f"Error al limpiar LLM provider: {e}")
        
        self.logger.info(f"Limpieza del agente {self.agent_name} completada")