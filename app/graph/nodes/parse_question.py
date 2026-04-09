from app.graph.state import InvestigatorState


def parse_question(state: InvestigatorState):
    question = state["question"]
    normalized = question.lower()

    period = "latest"
    if "yesterday" in normalized:
        period = "yesterday"
    elif "today" in normalized:
        period = "today"

    investigation_type = "metric_change"
    if any(word in normalized for word in ["drop", "decline", "down", "decrease", "fell"]):
        investigation_type = "metric_drop"
    elif any(word in normalized for word in ["increase", "up", "grew", "growth", "rose"]):
        investigation_type = "metric_increase"

    parsed = {
        "metric": "revenue",
        "period": period,
        "comparison_period": "previous_7_days_avg",
        "dimensions_to_check": ["device_type", "country", "provider", "payment_method"],
        "investigation_type": investigation_type,
    }
    trace = state["trace"] + [{
        "node": "parse_question",
        "message": f"Parsed question as revenue investigation ({investigation_type}, period={period}): {question}",
    }]
    return {"parsed_question": parsed, "trace": trace}
