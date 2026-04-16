from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage, AIMessage
from typing import Dict, Any, List
import json
from langgraph.types import interrupt
from src.utils.logger import get_logger
from .states import AgentState

logger = get_logger("nodes.py")

class NodeFunctions:
    def __init__(self, models: Dict[str, Any], system_prompt: str, tools: List[Any] = None, hitl_config: Dict[str, Any] = None):
        """
        Initialize NodeFunctions with a language model and tools.
        
        Args:
            models: Dictionary containing the language models (e.g., conversation_llm)
            tools: List of tools to bind to the LLM. If None, no tools will be bound.
            hitl_config: Configuration for human-in-the-loop interruption rules.
        """
        self.conversation_llm = models.get("conversation_llm")
        self.system_prompt = system_prompt
        self.tools = tools or []
        self._hitl_config = hitl_config or {}
        
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
        # Log detail for better observability (sanitizing for Windows Terminal encoding issues)
        if text_content:
            safe_text = text_content.encode("ascii", "ignore").decode("ascii")
            logger.info(f"Response last message (text): {safe_text}")
        
        if response.tool_calls:
            logger.info(f"Response tool calls: {[tc['name'] for tc in response.tool_calls]}")
        
        if not text_content and not response.tool_calls:
            logger.warning("LLM Response was empty (no text and no tool calls found).")
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

    async def hitl_gate(self, state: AgentState):
        """
        Human-In-The-Loop gate node.
        Checks if any tool calls require human approval and interrupts if necessary.
        """
        last_msg = state["messages_tools"][-1]
        if not isinstance(last_msg, AIMessage) or not last_msg.tool_calls:
            return state

        # Filter tool calls that need review based on injected hitl_config
        tools_to_review = [tc for tc in last_msg.tool_calls if tc["name"] in self._hitl_config]
        
        if not tools_to_review:
            return state

        logger.info(f"Interrupting for human review of tools: {[tc['name'] for tc in tools_to_review]}")
        
        # Trigger the interrupt
        # Client will resume with Command(resume={"decisions": [...]})
        human_response = interrupt({
            "action": "review_tools",
            "tool_calls": tools_to_review,
            "rules": self._hitl_config,
            "description": "Tool execution requires approval"
        })


        decisions = human_response.get("decisions", [])
        revised_tool_calls = []
        artificial_tool_messages = []
        
        for tool_call in last_msg.tool_calls:
            # Find the decision corresponding to this tool_call ID or name
            decision = None
            for d in decisions:
                d_id = d.get("id") if isinstance(d, dict) else getattr(d, "id", None)
                d_name = d.get("name") if isinstance(d, dict) else getattr(d, "name", None)
                if d_id == tool_call.get("id") or (d_name == tool_call.get("name") and d_name):
                    decision = d
                    break

            # Process decision
            d_type = (decision.get("type", "approve") if isinstance(decision, dict) else getattr(decision, "type", "approve")) if decision else "approve"
            
            if not decision or d_type == "approve":
                revised_tool_calls.append(tool_call)
            elif d_type == "edit":
                edited_call = tool_call.copy()
                edited_call["args"] = decision.get("edited_args") if isinstance(decision, dict) else getattr(decision, "edited_args", {})
                revised_tool_calls.append(edited_call)
                logger.info(f"Tool call {tool_call['name']} edited by human.")
            elif d_type == "reject":
                logger.info(f"Tool call {tool_call['name']} rejected by human.")
                msg = decision.get("message", "Tool execution rejected by user.") if isinstance(decision, dict) else getattr(decision, "message", "Tool execution rejected by user.")
                artificial_tool_messages.append(
                    ToolMessage(
                        content=msg,
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                        status="error"
                    )
                )


        # Update the AI message with either approved or edited tool calls
        last_msg.tool_calls = revised_tool_calls
        
        # Return updated state
        return {
            "messages_tools": [last_msg] + artificial_tool_messages
        }

    async def tool_node(self, state: AgentState, config: RunnableConfig):
        outputs = []
        for tool_call in state["messages_tools"][-1].tool_calls:
            tool_name = tool_call["name"]
            tool_id = tool_call["id"]
            
            try:
                logger.info(f"Invoking tool: {tool_name} with args: {tool_call['args']}")
                
                # Verify if tool exists (prevents KeyError from renames/refactors)
                if tool_name not in self.tools_by_name:
                    error_msg = f"Tool '{tool_name}' not found in current configuration. It might have been renamed or removed."
                    logger.error(error_msg)
                    outputs.append(ToolMessage(content=error_msg, name=tool_name, tool_call_id=tool_id, status="error"))
                    continue

                tool_result = await self.tools_by_name[tool_name].ainvoke(tool_call["args"], config=config)
                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_name,
                        tool_call_id=tool_id,
                    )
                )
            except Exception as e:
                error_msg = f"Error executing tool '{tool_name}': {str(e)}"
                logger.error(error_msg)
                outputs.append(
                    ToolMessage(
                        content=error_msg,
                        name=tool_name,
                        tool_call_id=tool_id,
                        status="error"
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
