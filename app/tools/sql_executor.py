from app.services.database import get_connection
from app.services.guardrails import validate_sql


def execute_sql(sql: str):
    validate_sql(sql)
    conn = get_connection()
    cursor = conn.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    return {
        "sql": sql,
        "columns": columns,
        "rows": [dict(zip(columns, row)) for row in rows],
        "row_count": len(rows),
    }
