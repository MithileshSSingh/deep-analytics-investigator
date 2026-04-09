from app.graph.state import InvestigatorState
from app.graph.nodes.parse_question import parse_question as parse_question_deterministic
from app.prompts.parse_question_prompt import build_parse_question_prompt
from app.services.llm_client import invoke_json, LLMUnavailableError, LLMParseError
from app.services.settings import LLM_ENABLED


ALLOWED_METRICS = {"revenue"}
ALLOWED_PERIODS = {"latest", "today", "yesterday"}
ALLOWED_INVESTIGATION_TYPES = {"metric_drop", "metric_increase", "metric_change"}
ALLOWED_DIMENSIONS = {"device_type", "country", "provider", "payment_method"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_ROUTES = {"revenue_investigation"}


def _validate_parsed_question(parsed):
    if not isinstance(parsed, dict):
        raise ValueError("Parsed question must be an object")

    metric = str(parsed.get("metric", "")).strip().lower()
    if metric not in ALLOWED_METRICS:
        raise ValueError("Unsupported or missing metric")

    period = str(parsed.get("period", "")).strip().lower()
    if period not in ALLOWED_PERIODS:
        raise ValueError("Unsupported or missing period")

    comparison_period = str(parsed.get("comparison_period", "")).strip() or "previous_7_days_avg"
    investigation_type = str(parsed.get("investigation_type", "")).strip().lower()
    if investigation_type not in ALLOWED_INVESTIGATION_TYPES:
        raise ValueError("Unsupported or missing investigation_type")

    route_candidates = parsed.get("route_candidates") or ["revenue_investigation"]
    if not isinstance(route_candidates, list):
        raise ValueError("route_candidates must be a list")
    normalized_routes = []
    for route in route_candidates:
        route = str(route).strip()
        if route in ALLOWED_ROUTES and route not in normalized_routes:
            normalized_routes.append(route)
    if not normalized_routes:
        normalized_routes = ["revenue_investigation"]

    dimensions = parsed.get("dimensions_to_check") or []
    if not isinstance(dimensions, list):
        raise ValueError("dimensions_to_check must be a list")
    normalized_dimensions = []
    for dimension in dimensions:
        dimension = str(dimension).strip()
        if dimension in ALLOWED_DIMENSIONS and dimension not in normalized_dimensions:
            normalized_dimensions.append(dimension)
    if not normalized_dimensions:
        normalized_dimensions = ["device_type", "country", "provider", "payment_method"]

    filters = parsed.get("filters") or {}
    if not isinstance(filters, dict):
        raise ValueError("filters must be an object")

    confidence = str(parsed.get("confidence", "medium")).strip().lower()
    if confidence not in ALLOWED_CONFIDENCE:
        confidence = "medium"

    needs_clarification = bool(parsed.get("needs_clarification", False))
    clarification_question = parsed.get("clarification_question")
    if clarification_question is not None:
        clarification_question = str(clarification_question).strip() or None

    return {
        "metric": metric,
        "route_candidates": normalized_routes,
        "period": period,
        "comparison_period": comparison_period,
        "dimensions_to_check": normalized_dimensions,
        "filters": filters,
        "investigation_type": investigation_type,
        "needs_clarification": needs_clarification,
        "clarification_question": clarification_question,
        "confidence": confidence,
    }


def parse_question_llm(state: InvestigatorState):
    question = state["question"]

    if not LLM_ENABLED:
        result = parse_question_deterministic(state)
        trace = result["trace"][:-1] + [{
            "node": "parse_question_llm",
            "message": "LLM parsing disabled; used deterministic parser",
        }] + [result["trace"][-1]]
        result["trace"] = trace
        return result

    prompt = build_parse_question_prompt(question)
    try:
        parsed = _validate_parsed_question(invoke_json(prompt))
        trace = state["trace"] + [{
            "node": "parse_question_llm",
            "message": f"Parsed question with LLM: {question}",
        }]
        return {"parsed_question": parsed, "trace": trace}
    except (LLMUnavailableError, LLMParseError, KeyError, TypeError, ValueError):
        result = parse_question_deterministic(state)
        trace = result["trace"][:-1] + [{
            "node": "parse_question_llm",
            "message": "LLM parse failed or unavailable; used deterministic fallback",
        }] + [result["trace"][-1]]
        result["trace"] = trace
        return result
