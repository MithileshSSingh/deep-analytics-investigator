from app.graph.state import InvestigatorState
from app.graph.nodes.generate_hypotheses import generate_hypotheses as generate_hypotheses_deterministic
from app.prompts.generate_hypotheses_prompt import build_generate_hypotheses_prompt
from app.services.llm_client import invoke_json, LLMUnavailableError, LLMParseError
from app.services.settings import LLM_ENABLED


ALLOWED_HYPOTHESIS_IDS = {
    "h1_payment_failure",
    "h2_mobile_segment",
    "h3_geo_specific_issue",
    "h0_general_decline",
}

DEFAULT_HYPOTHESIS_TITLES = {
    "h1_payment_failure": "Payment provider or payment method failure",
    "h2_mobile_segment": "Mobile revenue decline is a key driver",
    "h3_geo_specific_issue": "The decline is concentrated in India",
    "h0_general_decline": "General revenue weakness",
}

DEFAULT_HYPOTHESIS_REASONS = {
    "h1_payment_failure": "Provider-level revenue dropped sharply versus baseline.",
    "h2_mobile_segment": "Mobile segment underperformed baseline significantly.",
    "h3_geo_specific_issue": "Country-level analysis shows India materially below baseline.",
    "h0_general_decline": "No strong single-segment explanation emerged from current data.",
}


def _validate_hypotheses_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Hypotheses payload must be an object")

    hypotheses = payload.get("hypotheses", [])
    if not isinstance(hypotheses, list):
        raise ValueError("hypotheses must be a list")

    normalized = []
    seen = set()
    for item in hypotheses[:4]:
        if not isinstance(item, dict):
            raise ValueError("Each hypothesis must be an object")
        hypothesis_id = str(item.get("id", "")).strip()
        if hypothesis_id not in ALLOWED_HYPOTHESIS_IDS:
            raise ValueError(f"Unsupported hypothesis id: {hypothesis_id}")
        if hypothesis_id in seen:
            continue
        seen.add(hypothesis_id)
        title = str(item.get("title", "")).strip() or DEFAULT_HYPOTHESIS_TITLES[hypothesis_id]
        reason = str(item.get("reason", "")).strip() or DEFAULT_HYPOTHESIS_REASONS[hypothesis_id]
        normalized.append({"id": hypothesis_id, "title": title, "reason": reason})

    if any(item["id"] != "h0_general_decline" for item in normalized):
        normalized = [item for item in normalized if item["id"] != "h0_general_decline"]

    return normalized


def generate_hypotheses_llm(state: InvestigatorState):
    baseline = state.get("baseline_results", {})
    overall_delta = float(baseline.get("delta_pct", 0) or 0)

    if overall_delta >= 0:
        trace = state["trace"] + [{
            "node": "generate_hypotheses_llm",
            "message": "Skipped decline hypotheses because revenue did not decline",
        }]
        return {"hypotheses": [], "trace": trace}

    if not LLM_ENABLED:
        result = generate_hypotheses_deterministic(state)
        trace = result["trace"][:-1] + [{
            "node": "generate_hypotheses_llm",
            "message": "LLM hypothesis generation disabled; used deterministic hypotheses",
        }] + [result["trace"][-1]]
        result["trace"] = trace
        return result

    prompt = build_generate_hypotheses_prompt(
        question=state["question"],
        baseline_results=baseline,
        segment_results=state.get("segment_results", []),
    )

    try:
        hypotheses = _validate_hypotheses_payload(invoke_json(prompt))
        trace = state["trace"] + [{
            "node": "generate_hypotheses_llm",
            "message": f"Generated {len(hypotheses)} hypotheses with LLM",
        }]
        return {"hypotheses": hypotheses, "trace": trace}
    except (LLMUnavailableError, LLMParseError, ValueError, KeyError, TypeError):
        result = generate_hypotheses_deterministic(state)
        trace = result["trace"][:-1] + [{
            "node": "generate_hypotheses_llm",
            "message": "LLM hypothesis generation failed or unavailable; used deterministic fallback",
        }] + [result["trace"][-1]]
        result["trace"] = trace
        return result
