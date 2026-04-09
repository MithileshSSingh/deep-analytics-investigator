from app.graph.state import InvestigatorState
from app.graph.nodes.generate_report import generate_report as generate_report_deterministic
from app.prompts.generate_report_prompt import build_generate_report_prompt
from app.services.llm_client import invoke_json, LLMUnavailableError, LLMParseError
from app.services.settings import LLM_ENABLED


REQUIRED_REPORT_KEYS = {
    "summary",
    "what_changed",
    "top_findings",
    "likely_causes",
    "next_steps",
    "confidence",
}
VALID_CONFIDENCE = {"high", "medium", "low"}


def _validate_report_shape(report):
    if not isinstance(report, dict):
        raise ValueError("Report must be a JSON object")

    missing = REQUIRED_REPORT_KEYS - set(report.keys())
    if missing:
        raise ValueError(f"Missing report keys: {sorted(missing)}")

    if not isinstance(report["summary"], str) or not report["summary"].strip():
        raise ValueError("summary must be a non-empty string")

    for key in ("what_changed", "top_findings", "next_steps", "likely_causes"):
        if not isinstance(report[key], list):
            raise ValueError(f"{key} must be a list")

    if report["confidence"] not in VALID_CONFIDENCE:
        raise ValueError("confidence must be high, medium, or low")

    normalized_causes = []
    for item in report["likely_causes"][:3]:
        if not isinstance(item, dict):
            raise ValueError("Each likely cause must be an object")
        cause = str(item.get("cause", "")).strip()
        confidence = str(item.get("confidence", "")).strip().lower()
        evidence = item.get("evidence", [])
        if not cause:
            raise ValueError("likely cause is missing cause")
        if confidence not in VALID_CONFIDENCE:
            raise ValueError("likely cause confidence must be high, medium, or low")
        if not isinstance(evidence, list):
            raise ValueError("likely cause evidence must be a list")
        normalized_causes.append(
            {
                "cause": cause,
                "confidence": confidence,
                "evidence": [str(entry).strip() for entry in evidence if str(entry).strip()][:5],
            }
        )

    return {
        "summary": report["summary"].strip(),
        "what_changed": [str(item).strip() for item in report["what_changed"] if str(item).strip()][:6],
        "top_findings": [str(item).strip() for item in report["top_findings"] if str(item).strip()][:5],
        "likely_causes": normalized_causes,
        "next_steps": [str(item).strip() for item in report["next_steps"] if str(item).strip()][:5],
        "confidence": report["confidence"],
    }


def generate_report_llm(state: InvestigatorState):
    if not LLM_ENABLED:
        result = generate_report_deterministic(state)
        trace = result["trace"][:-1] + [{
            "node": "generate_report_llm",
            "message": "LLM report generation disabled; used deterministic report",
        }] + [result["trace"][-1]]
        result["trace"] = trace
        return result

    prompt = build_generate_report_prompt(
        question=state["question"],
        baseline_results=state.get("baseline_results", {}),
        ranked_hypotheses=state.get("ranked_hypotheses", []),
        segment_results=state.get("segment_results", []),
    )

    try:
        report = _validate_report_shape(invoke_json(prompt))
        trace = state["trace"] + [{
            "node": "generate_report_llm",
            "message": "Generated final report with LLM",
        }]
        return {"final_report": report, "trace": trace}
    except (LLMUnavailableError, LLMParseError, ValueError, KeyError, TypeError):
        result = generate_report_deterministic(state)
        trace = result["trace"][:-1] + [{
            "node": "generate_report_llm",
            "message": "LLM report generation failed or unavailable; used deterministic fallback",
        }] + [result["trace"][-1]]
        result["trace"] = trace
        return result
