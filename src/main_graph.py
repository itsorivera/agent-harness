from src.config.AgentDependenciesContainter import get_agent_general

async def get_agent():
    """Factory function for LangGraph CLI to load the graph."""
    agent_port = await get_agent_general()
    # The compiled graph is stored in the adapter
    return agent_port.agent_graph_compiled
