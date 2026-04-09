from typing import Any, Dict, List, TypedDict


class InvestigatorState(TypedDict, total=False):
    question: str
    parsed_question: Dict[str, Any]
    selected_route: Dict[str, Any]
    route_selection: Dict[str, Any]
    plan: Dict[str, Any]
    metric_definition: Dict[str, Any]
    baseline_results: Dict[str, Any]
    segment_results: List[Dict[str, Any]]
    evidence_artifacts: List[Dict[str, Any]]
    hypotheses: List[Dict[str, Any]]
    validated_hypotheses: List[Dict[str, Any]]
    ranked_hypotheses: List[Dict[str, Any]]
    executed_queries: List[Dict[str, Any]]
    final_report: Dict[str, Any]
    trace: List[Dict[str, Any]]
    errors: List[str]
