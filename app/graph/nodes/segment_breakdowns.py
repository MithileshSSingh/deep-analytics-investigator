from app.graph.state import InvestigatorState
from app.tools.sql_executor import execute_sql
from app.services.database import build_segment_queries
from app.services.evidence_builder import build_evidence_artifacts


def run_segment_breakdowns(state: InvestigatorState):
    period = state.get("parsed_question", {}).get("period", "latest")
    queries = build_segment_queries(period=period)
    segment_results = []
    executed_queries = list(state["executed_queries"])

    for dimension, sql in queries.items():
        result = execute_sql(sql)
        segment_results.append({"dimension": dimension, "rows": result["rows"]})
        executed_queries.append({
            "name": f"segment_{dimension}",
            "sql": sql,
            "row_count": result["row_count"],
        })

    route_name = state.get("selected_route", {}).get("name", "revenue_investigation")
    evidence_artifacts = build_evidence_artifacts(
        state.get("baseline_results", {}),
        segment_results,
        route=route_name,
    )

    trace = state["trace"] + [{
        "node": "run_segment_breakdowns",
        "message": f"Executed segment breakdown queries for revenue analysis (period={period})",
    }]
    return {
        "segment_results": segment_results,
        "evidence_artifacts": evidence_artifacts,
        "executed_queries": executed_queries,
        "trace": trace,
    }
