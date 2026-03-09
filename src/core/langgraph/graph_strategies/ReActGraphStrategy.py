from langgraph.graph import StateGraph, START, END
from src.core.langgraph.states import AgentState
from src.core.ports.graph_strategy_port import GraphStrategyPort

class ReActGraphStrategy(GraphStrategyPort):

    def get_required_node_functions(self):
        return ["call_model", "tool_node", "should_continue"]

    def build_graph(self, state_schema, node_functions):
        builder = StateGraph(AgentState)
        builder.add_node("agent", node_functions["call_model"])
        builder.add_node("tools", node_functions["tool_node"])

        builder.add_edge(START, "agent")
        builder.add_conditional_edges(
            "agent",
            node_functions["should_continue"],
            {
                "continue": "tools",
                "end": END,
            },
        )
        builder.add_edge("tools", "agent")

        return builder