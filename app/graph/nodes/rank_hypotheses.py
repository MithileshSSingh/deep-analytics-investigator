from app.graph.state import InvestigatorState


def _safe_num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_worst_segments(segment_results):
    worst = {}
    for block in segment_results:
        dimension = block.get("dimension")
        rows = block.get("rows", [])
        valid_rows = [r for r in rows if r.get("delta_pct") is not None]
        if valid_rows:
            worst[dimension] = sorted(valid_rows, key=lambda r: _safe_num(r.get("delta_pct"), 0))[0]
    return worst


def rank_hypotheses_node(state: InvestigatorState):
    hypotheses = state.get("hypotheses", [])
    validated_map = {item["id"]: item for item in state.get("validated_hypotheses", [])}
    worst_segments = _get_worst_segments(state.get("segment_results", []))
    ranked = []

    for hypothesis in hypotheses:
        hypothesis_id = hypothesis.get("id", "")
        score = 0
        reasons = []
        validated_item = validated_map.get(hypothesis_id)

        if validated_item:
            evidence = validated_item.get("evidence", [])
            evidence_count = len(evidence)
            if validated_item.get("status") == "supported":
                score += 35
                reasons.append("validation query support")
            else:
                score += 5
                reasons.append("limited validation support")
            score += min(evidence_count * 8, 24)
            if evidence_count:
                reasons.append(f"{evidence_count} evidence rows retained")
            if any("payments=" in e for e in evidence):
                score += 8
                reasons.append("meaningful payment volume in evidence")
            if any("provider=razorpay" in e for e in evidence):
                score += 15
                reasons.append("evidence includes razorpay cluster")
            if any("method=upi" in e for e in evidence):
                score += 12
                reasons.append("evidence includes upi cluster")
            if any("country=India" in e for e in evidence):
                score += 10
                reasons.append("evidence includes India cluster")
            if any("device=mobile" in e for e in evidence):
                score += 10
                reasons.append("evidence includes mobile cluster")
            if any("error=" in e for e in evidence):
                score += 10
                reasons.append("evidence includes failure codes")

        provider_worst = worst_segments.get("provider")
        method_worst = worst_segments.get("payment_method")
        device_worst = worst_segments.get("device_type")
        country_worst = worst_segments.get("country")

        if hypothesis_id == "h1_payment_failure":
            if provider_worst and _safe_num(provider_worst.get("delta_pct")) < -8:
                score += 18
                reasons.append("provider delta strongly negative")
            if method_worst and _safe_num(method_worst.get("delta_pct")) < -8:
                score += 18
                reasons.append("payment method delta strongly negative")

        if hypothesis_id == "h2_mobile_segment":
            if device_worst and str(device_worst.get("segment")).lower() == "mobile":
                score += 25
                reasons.append("mobile is worst-performing device segment")

        if hypothesis_id == "h3_geo_specific_issue":
            if country_worst and str(country_worst.get("segment")).lower() == "india":
                score += 25
                reasons.append("India is worst-performing geography segment")

        if hypothesis_id in {"h1_payment_failure", "h2_mobile_segment", "h3_geo_specific_issue"}:
            score += 8
            reasons.append("specific explanation")

        if hypothesis_id == "h0_general_decline":
            score -= 15
            reasons.append("generic fallback explanation")

        if validated_item and not validated_item.get("evidence"):
            score -= 20
            reasons.append("missing retained evidence")

        ranked.append({
            "id": hypothesis_id,
            "title": hypothesis.get("title", "Unknown cause"),
            "score": score,
            "reasons": reasons,
            "validated_item": validated_item,
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    trace = state["trace"] + [{
        "node": "rank_hypotheses",
        "message": f"Ranked {len(ranked)} hypotheses by evidence strength",
    }]
    return {"ranked_hypotheses": ranked, "trace": trace}
