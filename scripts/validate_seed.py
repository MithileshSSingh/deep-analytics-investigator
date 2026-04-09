from pathlib import Path
import duckdb

DB_PATH = Path("data/demo.duckdb")


def run_query(conn, sql: str):
    return conn.execute(sql).fetchdf()


def main():
    conn = duckdb.connect(str(DB_PATH))
    print(run_query(conn, "SELECT COUNT(*) AS count FROM payments"))
    print(run_query(conn, """
    WITH daily_revenue AS (
      SELECT DATE(payment_timestamp) AS day,
             SUM(CASE WHEN payment_status = 'success' THEN amount ELSE 0 END) AS revenue
      FROM payments
      GROUP BY 1
    ), latest_day AS (
      SELECT MAX(day) AS current_day FROM daily_revenue
    ), baseline AS (
      SELECT AVG(revenue) AS baseline_revenue
      FROM daily_revenue
      WHERE day >= (SELECT current_day - 7 FROM latest_day)
        AND day < (SELECT current_day FROM latest_day)
    )
    SELECT d.day, d.revenue AS current_revenue, b.baseline_revenue,
           ROUND(((d.revenue - b.baseline_revenue) / NULLIF(b.baseline_revenue, 0)) * 100, 2) AS delta_pct
    FROM daily_revenue d
    CROSS JOIN baseline b
    WHERE d.day = (SELECT current_day FROM latest_day)
    """))
    conn.close()


if __name__ == "__main__":
    main()
