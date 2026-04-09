from langgraph.graph import StateGraph, END
from app.graph.state import InvestigatorState
from app.graph.nodes.parse_question_llm import parse_question_llm
from app.graph.nodes.resolve_metric import resolve_metric
from app.graph.nodes.baseline_queries import run_baseline_queries
from app.graph.nodes.segment_breakdowns import run_segment_breakdowns
from app.graph.nodes.generate_hypotheses import generate_hypotheses
from app.graph.nodes.validate_hypotheses import validate_hypotheses
from app.graph.nodes.rank_hypotheses import rank_hypotheses_node
from app.graph.nodes.generate_report_llm import generate_report_llm


def build_workflow():
    graph = StateGraph(InvestigatorState)
    graph.add_node("parse_question", parse_question_llm)
    graph.add_node("resolve_metric", resolve_metric)
    graph.add_node("run_baseline_queries", run_baseline_queries)
    graph.add_node("run_segment_breakdowns", run_segment_breakdowns)
    graph.add_node("generate_hypotheses", generate_hypotheses)
    graph.add_node("validate_hypotheses", validate_hypotheses)
    graph.add_node("rank_hypotheses", rank_hypotheses_node)
    graph.add_node("generate_report", generate_report_llm)

    graph.set_entry_point("parse_question")
    graph.add_edge("parse_question", "resolve_metric")
    graph.add_edge("resolve_metric", "run_baseline_queries")
    graph.add_edge("run_baseline_queries", "run_segment_breakdowns")
    graph.add_edge("run_segment_breakdowns", "generate_hypotheses")
    graph.add_edge("generate_hypotheses", "validate_hypotheses")
    graph.add_edge("validate_hypotheses", "rank_hypotheses")
    graph.add_edge("rank_hypotheses", "generate_report")
    graph.add_edge("generate_report", END)
    return graph.compile()


workflow = build_workflow()


def run_investigation(question: str):
    initial_state: InvestigatorState = {
        "question": question,
        "trace": [],
        "executed_queries": [],
        "errors": [],
    }
    return workflow.invoke(initial_state)
