from langgraph.graph import StateGraph, START, END

from app.graph.state import GraphState
from app.graph.nodes import check_evidence
from app.agents.retrieval_agent import retrieval_agent
from app.agents.answer_agent import answer_agent
from app.agents.conflict_detector import detect_conflicts
from app.agents.evidence_agent import build_evidence


def route_after_evidence_check(state):
    if state.get("evidence_sufficient") is True:
        return "generate"

    return "end"


def build_graph():
    graph = StateGraph(GraphState)

    # Nodes
    graph.add_node("retrieve", retrieval_agent)
    graph.add_node("detect_conflicts", detect_conflicts)
    graph.add_node("check_evidence", check_evidence)
    graph.add_node("generate", answer_agent)
    graph.add_node("build_evidence", build_evidence)

    # Main flow
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "detect_conflicts")
    graph.add_edge("detect_conflicts", "check_evidence")
    graph.add_conditional_edges(
        "check_evidence",
        route_after_evidence_check,
        {
            "generate": "generate",
            "end": END,
        },
    )
    graph.add_edge("generate", "build_evidence")
    graph.add_edge("build_evidence", END)

    return graph.compile()
