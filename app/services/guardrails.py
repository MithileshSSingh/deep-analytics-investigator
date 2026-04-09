FORBIDDEN_SQL = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"]


def validate_sql(sql: str):
    normalized = sql.upper().strip()

    if not normalized.startswith("SELECT") and not normalized.startswith("WITH"):
        raise ValueError("Only read-only SELECT/WITH queries are allowed.")

    for keyword in FORBIDDEN_SQL:
        if keyword in normalized:
            raise ValueError(f"Forbidden SQL keyword detected: {keyword}")

    if ";" in normalized[:-1]:
        raise ValueError("Multiple SQL statements are not allowed.")
