from typing import Any, Dict, List


def safe_num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def format_money(value: Any) -> str:
    return f"${safe_num(value):,.2f}"


def format_pct(value: Any) -> str:
    return f"{safe_num(value):.2f}%"


def format_evidence_row(row: Dict[str, Any]) -> str:
    parts = []
    if row.get("provider"):
        parts.append(f"provider={row['provider']}")
    if row.get("payment_method"):
        parts.append(f"method={row['payment_method']}")
    if row.get("country"):
        parts.append(f"country={row['country']}")
    if row.get("device_type"):
        parts.append(f"device={row['device_type']}")
    if row.get("total_payments") is not None:
        parts.append(f"payments={row['total_payments']}")
    if row.get("current_success_rate") is not None and row.get("baseline_success_rate") is not None:
        parts.append(f"success rate {format_pct(row['current_success_rate'])} vs baseline {format_pct(row['baseline_success_rate'])}")
    if row.get("success_rate_delta") is not None:
        parts.append(f"delta {format_pct(row['success_rate_delta'])}")
    if row.get("error_code"):
        parts.append(f"error={row['error_code']}")
    if row.get("failure_count") is not None:
        parts.append(f"failures={row['failure_count']}")
    return ", ".join(parts)


def pick_interesting_segment(rows: List[Dict[str, Any]], preferred=None):
    if not rows:
        return None
    preferred = preferred or []
    enriched = []
    for row in rows:
        delta = safe_num(row.get("delta_pct"), 0)
        current_revenue = safe_num(row.get("current_revenue"), 0)
        baseline_revenue = safe_num(row.get("baseline_revenue"), 0)
        weight = max(current_revenue, baseline_revenue)
        bonus = 0
        if str(row.get("segment")) in preferred:
            bonus += 2000
        score = abs(delta) * weight + bonus
        enriched.append((score, row))
    enriched.sort(key=lambda x: x[0], reverse=True)
    return enriched[0][1]


def extract_segment_highlights(segment_results: List[Dict[str, Any]]) -> List[str]:
    preference_map = {
        "device_type": ["mobile"],
        "country": ["India"],
        "provider": ["razorpay"],
        "payment_method": ["upi"],
    }
    findings = []
    for block in segment_results:
        dimension = block.get("dimension")
        rows = block.get("rows", [])
        interesting = pick_interesting_segment(rows, preference_map.get(dimension, []))
        if not interesting:
            continue
        delta_value = safe_num(interesting.get("delta_pct"), 0)
        if delta_value > -6:
            continue
        findings.append(
            f"{dimension}: {interesting.get('segment', 'unknown')} dropped to {format_money(interesting.get('current_revenue', 0))} from {format_money(interesting.get('baseline_revenue', 0))} ({format_pct(delta_value)})."
        )
    return findings
