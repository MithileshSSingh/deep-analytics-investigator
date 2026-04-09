from app.graph.state import InvestigatorState
from app.tools.sql_executor import execute_sql
from app.services.database import build_validation_query_payment_success, build_validation_query_failed_payment_errors, build_validation_query_target_cluster, build_segment_delta_query
from app.services.report_formatter import format_evidence_row

HYPOTHESIS_QUERY_MAP = {
    "h1_payment_failure": [
        "payment_success_comparison",
        "payment_error_codes",
        "payment_target_cluster",
    ],
    "h2_mobile_segment": [
        "device_segment_delta",
    ],
    "h3_geo_specific_issue": [
        "country_segment_delta",
    ],
}


def _query_sql(query_name: str, period: str) -> str:
    if query_name == "payment_success_comparison":
        return build_validation_query_payment_success(period=period)
    if query_name == "payment_error_codes":
        return build_validation_query_failed_payment_errors(period=period)
    if query_name == "payment_target_cluster":
        return build_validation_query_target_cluster(period=period)
    if query_name == "device_segment_delta":
        return build_segment_delta_query("device_type", period=period)
    if query_name == "country_segment_delta":
        return build_segment_delta_query("country", period=period)
    raise ValueError(f"Unsupported validation query: {query_name}")


def _select_evidence_rows(hypothesis_id: str, query_name: str, rows):
    if not rows:
        return []

    if query_name == "payment_target_cluster":
        return rows[:1]

    if hypothesis_id == "h1_payment_failure":
        targeted = [
            row for row in rows
            if str(row.get("provider", "")).lower() == "razorpay"
            and str(row.get("payment_method", "")).lower() == "upi"
            and str(row.get("country", "")).lower() == "india"
            and str(row.get("device_type", "")).lower() == "mobile"
        ]
        return (targeted + rows)[:2]

    if hypothesis_id == "h2_mobile_segment":
        targeted = [row for row in rows if str(row.get("segment", "")).lower() == "mobile"]
        return (targeted or rows[:1])[:1]

    if hypothesis_id == "h3_geo_specific_issue":
        targeted = [row for row in rows if str(row.get("segment", "")).lower() == "india"]
        return (targeted or rows[:1])[:1]

    return rows[:2]


def validate_hypotheses(state: InvestigatorState):
    hypotheses = state.get("hypotheses", [])
    validated = []
    executed_queries = list(state["executed_queries"])
    period = state.get("parsed_question", {}).get("period", "latest")

    for hypothesis in hypotheses:
        hypothesis_id = hypothesis["id"]
        query_names = HYPOTHESIS_QUERY_MAP.get(hypothesis_id, [])
        evidence = []
        support_score = 0

        for query_name in query_names:
            sql = _query_sql(query_name, period=period)
            result = execute_sql(sql)
            executed_queries.append({
                "name": query_name,
                "sql": sql,
                "row_count": result["row_count"],
            })
            selected_rows = _select_evidence_rows(hypothesis_id, query_name, result["rows"])
            formatted_rows = [format_evidence_row(row) for row in selected_rows]
            evidence.extend([row for row in formatted_rows if row])
            if selected_rows:
                support_score += 1

        status = "supported" if support_score >= 1 and evidence else "weak_support"
        validated.append({
            "id": hypothesis_id,
            "title": hypothesis["title"],
            "status": status,
            "evidence": evidence[:5],
        })

    trace = state["trace"] + [{
        "node": "validate_hypotheses",
        "message": f"Validated {len(validated)} hypotheses for period={period}",
    }]
    return {"validated_hypotheses": validated, "executed_queries": executed_queries, "trace": trace}
