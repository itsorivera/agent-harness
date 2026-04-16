from langgraph.graph import StateGraph, START, END
from ..states import AgentState
from ..graph_strategy_port import GraphStrategyPort

class ReActGraphStrategy(GraphStrategyPort):

    def get_required_node_functions(self):
        return ["call_model", "tool_node", "should_continue", "hitl_gate"]

    def build_graph(self, state_schema, node_functions):
        builder = StateGraph(AgentState)
        builder.add_node("agent", node_functions["call_model"])
        builder.add_node("hitl_gate", node_functions["hitl_gate"])
        builder.add_node("tools", node_functions["tool_node"])

        builder.add_edge(START, "agent")
        builder.add_conditional_edges(
            "agent",
            node_functions["should_continue"],
            {
                "continue": "hitl_gate",
                "end": END,
            },
        )
        builder.add_edge("hitl_gate", "tools")
        builder.add_edge("tools", "agent")

        return builder
