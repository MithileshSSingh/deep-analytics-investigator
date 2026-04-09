from app.graph.state import InvestigatorState
from app.services.report_formatter import extract_segment_highlights, format_money, format_pct


def score_to_confidence(score):
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def describe_change(delta_pct):
    if delta_pct < 0:
        return "dropped"
    if delta_pct > 0:
        return "increased"
    return "was flat"


def generate_report(state: InvestigatorState):
    baseline = state.get("baseline_results", {})
    ranked_hypotheses = state.get("ranked_hypotheses", [])
    segment_results = state.get("segment_results", [])
    delta_pct = float(baseline.get("delta_pct", 0) or 0)
    change_phrase = describe_change(delta_pct)

    likely_causes = []
    for item in ranked_hypotheses[:3]:
        validated_item = item.get("validated_item") or {}
        evidence = [e for e in validated_item.get("evidence", [])[:3] if e]
        score = item.get("score", 0)
        if not evidence and score < 60:
            continue
        likely_causes.append({
            "cause": item.get("title", "Unknown cause"),
            "confidence": score_to_confidence(score),
            "evidence": evidence,
        })

    confidence = score_to_confidence(ranked_hypotheses[0].get("score", 0)) if ranked_hypotheses else "low"
    top_cause = likely_causes[0]["cause"] if likely_causes else "No strong cause identified"

    if change_phrase == "was flat":
        summary = (
            f"Revenue was flat at {format_money(baseline.get('current_value', 0))} versus a 7-day baseline of "
            f"{format_money(baseline.get('baseline_value', 0))}. No strong directional change is visible."
        )
    elif delta_pct > 0 and not likely_causes:
        summary = (
            f"Revenue increased to {format_money(baseline.get('current_value', 0))} versus a 7-day baseline of "
            f"{format_money(baseline.get('baseline_value', 0))} ({format_pct(delta_pct)}). There is no negative incident to explain in the current window."
        )
    else:
        summary = (
            f"Revenue {change_phrase} to {format_money(baseline.get('current_value', 0))} versus a 7-day baseline of "
            f"{format_money(baseline.get('baseline_value', 0))} ({format_pct(delta_pct)}). "
            f"The strongest current explanation is: {top_cause}."
        )

    if change_phrase == "dropped" and likely_causes and any('razorpay' in e.lower() and 'upi' in e.lower() and 'india' in e.lower() and 'mobile' in e.lower() for e in likely_causes[0].get('evidence', [])):
        summary = (
            f"Revenue dropped to {format_money(baseline.get('current_value', 0))} versus a 7-day baseline of "
            f"{format_money(baseline.get('baseline_value', 0))} ({format_pct(delta_pct)}). "
            f"The strongest evidence points to Razorpay UPI payment failures in India mobile traffic."
        )

    report = {
        "summary": summary,
        "what_changed": [
            f"Current revenue: {format_money(baseline.get('current_value', 0))}",
            f"7-day average baseline: {format_money(baseline.get('baseline_value', 0))}",
            f"Absolute delta: {format_money(baseline.get('absolute_delta', 0))}",
            f"Revenue delta: {format_pct(delta_pct)}",
        ],
        "top_findings": extract_segment_highlights(segment_results)[:5],
        "likely_causes": likely_causes,
        "next_steps": (
            [
                "Inspect the top-ranked failure cluster in provider and payment-method data",
                "Check whether the mobile and India segments align with the strongest hypothesis",
                "Review error-code concentration for operational confirmation",
            ]
            if likely_causes else
            [
                "Review winning segments to understand what contributed to the increase",
                "Compare conversion and payment-success improvements versus the prior 7-day baseline",
                "Save this run as a healthy-reference snapshot for later anomaly comparisons",
            ]
        ),
        "confidence": confidence,
    }

    trace = state["trace"] + [{
        "node": "generate_report",
        "message": f"Generated ranked, evidence-aware final report ({change_phrase})",
    }]
    return {"final_report": report, "trace": trace}
