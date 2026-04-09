from app.graph.state import InvestigatorState


def generate_hypotheses(state: InvestigatorState):
    segment_results = state.get("segment_results", [])
    baseline = state.get("baseline_results", {})
    overall_delta = float(baseline.get("delta_pct", 0) or 0)
    hypotheses = []

    if overall_delta >= 0:
        trace = state["trace"] + [{
            "node": "generate_hypotheses",
            "message": "Skipped decline hypotheses because revenue did not decline",
        }]
        return {"hypotheses": [], "trace": trace}

    for block in segment_results:
        dimension = block.get("dimension")
        rows = block.get("rows", [])
        for row in rows[:3]:
            delta = row.get("delta_pct")
            if delta is not None and float(delta) < -8:
                if dimension == "provider":
                    hypotheses.append({
                        "id": "h1_payment_failure",
                        "title": "Payment provider or payment method failure",
                        "reason": "Provider-level revenue dropped sharply versus baseline.",
                    })
                    break
                if dimension == "device_type" and str(row.get("segment")).lower() == "mobile":
                    hypotheses.append({
                        "id": "h2_mobile_segment",
                        "title": "Mobile revenue decline is a key driver",
                        "reason": "Mobile segment underperformed baseline significantly.",
                    })
                    break
                if dimension == "country" and str(row.get("segment")).lower() == "india":
                    hypotheses.append({
                        "id": "h3_geo_specific_issue",
                        "title": "The decline is concentrated in India",
                        "reason": "Country-level analysis shows India materially below baseline.",
                    })
                    break

    if not hypotheses:
        hypotheses.append({
            "id": "h0_general_decline",
            "title": "General revenue weakness",
            "reason": "No strong single-segment explanation emerged from current data.",
        })

    deduped = {item["id"]: item for item in hypotheses}
    result = list(deduped.values())
    trace = state["trace"] + [{
        "node": "generate_hypotheses",
        "message": f"Generated {len(result)} hypotheses",
    }]
    return {"hypotheses": result, "trace": trace}
