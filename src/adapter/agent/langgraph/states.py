from typing_extensions import TypedDict
from typing import Annotated, Sequence, List, Dict, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

def merge_explanations(left: list, right: list) -> list:
    """Helper to append explanations to the history."""
    return (left or []) + (right or [])

class AgentState(TypedDict):
    """The state of the agent."""
    messages_tools: Annotated[Sequence[BaseMessage], add_messages]
    messages: Annotated[Sequence[BaseMessage], add_messages]
    explanations: Annotated[list, merge_explanations]
    notes: str
    human_call_flag: bool