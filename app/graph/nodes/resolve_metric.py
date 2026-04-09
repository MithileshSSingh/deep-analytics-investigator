from app.graph.state import InvestigatorState
from app.tools.metric_registry import METRIC_REGISTRY
from app.registries.route_registry import ROUTE_REGISTRY


def resolve_metric(state: InvestigatorState):
    metric_name = state["parsed_question"]["metric"]
    metric_definition = METRIC_REGISTRY[metric_name]
    route_name = "revenue_investigation"
    route_definition = ROUTE_REGISTRY[route_name]
    plan = {
        "route": route_name,
        "baseline_query_families": route_definition["baseline_query_families"],
        "segment_query_families": route_definition["segment_query_families"],
        "validation_query_families": route_definition["validation_query_families"],
    }
    trace = state["trace"] + [{
        "node": "resolve_metric",
        "message": f"Resolved metric '{metric_name}' and selected route '{route_name}'",
    }]
    return {
        "metric_definition": metric_definition,
        "selected_route": route_definition,
        "plan": plan,
        "trace": trace,
    }
