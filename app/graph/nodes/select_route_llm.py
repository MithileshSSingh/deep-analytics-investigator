from app.graph.state import InvestigatorState
from app.graph.nodes.resolve_metric import resolve_metric as resolve_metric_deterministic
from app.prompts.select_route_prompt import build_select_route_prompt
from app.registries.route_registry import ROUTE_REGISTRY
from app.services.llm_client import invoke_json, LLMUnavailableError, LLMParseError
from app.services.settings import LLM_ENABLED
from app.tools.metric_registry import METRIC_REGISTRY


VALID_CONFIDENCE = {"low", "medium", "high"}


def _validate_route_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Route payload must be an object")

    route_name = str(payload.get("route_name", "")).strip()
    if route_name not in ROUTE_REGISTRY:
        raise ValueError("Unsupported route_name")

    confidence = str(payload.get("confidence", "medium")).strip().lower()
    if confidence not in VALID_CONFIDENCE:
        confidence = "medium"

    reason = str(payload.get("reason", "")).strip() or f"Selected route {route_name}"
    return {
        "route_name": route_name,
        "reason": reason,
        "confidence": confidence,
    }


def _build_result(state: InvestigatorState, route_name: str, trace_message: str, selector_reason: str | None = None):
    metric_name = state["parsed_question"]["metric"]
    metric_definition = METRIC_REGISTRY[metric_name]
    route_definition = ROUTE_REGISTRY[route_name]
    plan = {
        "route": route_name,
        "baseline_query_families": route_definition["baseline_query_families"],
        "segment_query_families": route_definition["segment_query_families"],
        "validation_query_families": route_definition["validation_query_families"],
    }
    trace = state["trace"] + [{
        "node": "select_route_llm",
        "message": trace_message,
    }]
    result = {
        "metric_definition": metric_definition,
        "selected_route": route_definition,
        "plan": plan,
        "trace": trace,
    }
    if selector_reason:
        result["route_selection"] = {
            "route_name": route_name,
            "reason": selector_reason,
        }
    return result


def select_route_llm(state: InvestigatorState):
    parsed_question = state["parsed_question"]

    if not LLM_ENABLED:
        result = resolve_metric_deterministic(state)
        trace = result["trace"][:-1] + [{
            "node": "select_route_llm",
            "message": "LLM route selection disabled; used deterministic route resolver",
        }] + [result["trace"][-1]]
        result["trace"] = trace
        return result

    prompt = build_select_route_prompt(parsed_question, ROUTE_REGISTRY)
    try:
        selection = _validate_route_payload(invoke_json(prompt))
        return _build_result(
            state,
            route_name=selection["route_name"],
            trace_message=f"Selected route with LLM: {selection['route_name']}",
            selector_reason=selection["reason"],
        )
    except (LLMUnavailableError, LLMParseError, ValueError, KeyError, TypeError):
        result = resolve_metric_deterministic(state)
        trace = result["trace"][:-1] + [{
            "node": "select_route_llm",
            "message": "LLM route selection failed or unavailable; used deterministic fallback",
        }] + [result["trace"][-1]]
        result["trace"] = trace
        return result
