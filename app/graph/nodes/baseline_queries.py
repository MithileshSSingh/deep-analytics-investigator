from app.graph.state import InvestigatorState
from app.tools.sql_executor import execute_sql
from app.services.database import build_revenue_baseline_query


def run_baseline_queries(state: InvestigatorState):
    period = state.get("parsed_question", {}).get("period", "latest")
    sql = build_revenue_baseline_query(period=period)
    result = execute_sql(sql)
    baseline_results = result["rows"][0] if result["rows"] else {
        "current_value": 0,
        "baseline_value": 0,
        "absolute_delta": 0,
        "delta_pct": 0,
    }
    trace = state["trace"] + [{
        "node": "run_baseline_queries",
        "message": f"Executed baseline revenue comparison query for period={period}",
    }]
    executed_queries = state["executed_queries"] + [{
        "name": "baseline_revenue",
        "sql": sql,
        "row_count": result["row_count"],
    }]
    return {"baseline_results": baseline_results, "executed_queries": executed_queries, "trace": trace}
