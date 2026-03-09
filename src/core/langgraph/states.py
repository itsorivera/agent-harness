from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage, AIMessage
from typing import Dict, Any, List
import json
from src.utils.Logger import setup_logger
from .states import AgentState

logger = setup_logger("nodes.py")

class NodeFunctions:
    def _init_(self, models: Dict[str, Any], system_prompt: str, tools: List[Any] = None):
        """
        Initialize NodeFunctions with a language model and tools.
        
        Args:
            models: Dictionary containing the language models (e.g., conversation_llm)
            tools: List of tools to bind to the LLM. If None, no tools will be bound.
        """
        self.conversation_llm = models.get("conversation_llm")
        self.system_prompt = system_prompt
        self.tools = tools or []
        
        # Bind tools to the LLM if tools are provided. #TODO revisar logica para bindear tools
        if self.tools:
            self.conversation_llm = self.conversation_llm.bind_tools(self.tools)
            self.tools_by_name = {tool.name: tool for tool in self.tools}
            logger.info(f"Bound tools to conversation LLM: {[tool.name for tool in self.tools]}")
        else:
            self.tools_by_name = {}
            logger.info("No tools bound to conversation LLM.")

    def call_model(self, state: AgentState, config: RunnableConfig):
        system_prompt = SystemMessage(content=self.system_prompt)
        #system_prompt = SystemMessage(content=CREDIT_CARD_AGENT_PROMPT.render())
        response = self.conversation_llm.invoke([system_prompt] + state["messages_tools"], config)
        # Extrae solo el texto de la respuesta, ignorando posibles tool_use blocks
        text_content = ""
        if isinstance(response.content, str):
            text_content = response.content
        elif isinstance(response.content, list):
            # Filtra y concatena solo los bloques de texto
            text_content = " ".join([
                block.get("text", "")
                for block in response.content
                if isinstance(block, dict) and block.get("type") == "text"
            ])
        logger.info(f"Response last message: {text_content}")
        return {"messages_tools": [response],
                "messages": [
                    HumanMessage(state["messages_tools"][-1].content),
                    AIMessage(
                        content=text_content,
                        response_metadata=response.response_metadata,
                        usage_metadata=response.usage_metadata, #TODO meter en una funcion el formato de salida
                    ), 
                ],
            }

    async def tool_node(self, state: AgentState):
        outputs = []
        for tool_call in state["messages_tools"][-1].tool_calls:
            logger.info(f"Invoking tool: {tool_call['name']} with args: {tool_call['args']}")
            tool_result = await self.tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages_tools": outputs}

    def should_continue(self, state: AgentState):
        messages = state["messages_tools"]
        last_message = messages[-1]
        logger.info(f"last_message.tool_calls = {last_message.tool_calls}")
        if not last_message.tool_calls:
            logger.info("No tool calls found, ending workflow.")
            return "end"
        else:
            logger.info("Tool calls found, continuing workflow.")
            return "continue"

    def human_in_the_loop(self, state: AgentState) -> dict:
        """
        Escalate to human support agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with escalation notes
        """
        print("\n[Node: human_in_the_loop]")
        print("Simulated: Escalating to a human support agent. (End of automation)")
        state["notes"] += "\n[human_in_the_loop] Issue escalated to a human agent."
        return state