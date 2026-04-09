import duckdb
from pathlib import Path

DB_PATH = Path("data/demo.duckdb")
_connection = None


def get_connection():
    global _connection
    if _connection is None:
        _connection = duckdb.connect(str(DB_PATH))
    return _connection


def _target_day_cte(period: str = "latest") -> str:
    if period == "yesterday":
        return "SELECT MAX(DATE(payment_timestamp)) - 1 AS current_day FROM payments"
    return "SELECT MAX(DATE(payment_timestamp)) AS current_day FROM payments"


def build_revenue_baseline_query(period: str = "latest"):
    return f"""
    WITH target_day AS (
      {_target_day_cte(period)}
    ),
    daily_revenue AS (
      SELECT
        DATE(payment_timestamp) AS day,
        SUM(CASE WHEN payment_status = 'success' THEN amount ELSE 0 END) AS revenue
      FROM payments
      GROUP BY 1
    ),
    baseline AS (
      SELECT AVG(revenue) AS baseline_revenue
      FROM daily_revenue
      WHERE day >= (SELECT current_day - 7 FROM target_day)
        AND day < (SELECT current_day FROM target_day)
    )
    SELECT
      d.day AS current_day,
      d.revenue AS current_value,
      b.baseline_revenue AS baseline_value,
      ROUND(d.revenue - b.baseline_revenue, 2) AS absolute_delta,
      ROUND(((d.revenue - b.baseline_revenue) / NULLIF(b.baseline_revenue, 0)) * 100, 2) AS delta_pct
    FROM daily_revenue d
    CROSS JOIN baseline b
    WHERE d.day = (SELECT current_day FROM target_day)
    """


ALLOWED_DIMENSIONS = {"device_type", "country", "provider", "payment_method"}


def build_segment_delta_query(dimension: str, period: str = "latest"):
    if dimension not in ALLOWED_DIMENSIONS:
        raise ValueError(f"Unsupported dimension: {dimension}")

    return f"""
    WITH target_day AS (
      {_target_day_cte(period)}
    ),
    current_period AS (
      SELECT
        {dimension} AS segment,
        SUM(CASE WHEN payment_status = 'success' THEN amount ELSE 0 END) AS current_revenue
      FROM payments
      WHERE DATE(payment_timestamp) = (SELECT current_day FROM target_day)
      GROUP BY 1
    ),
    baseline_period AS (
      SELECT
        {dimension} AS segment,
        AVG(daily_revenue) AS baseline_revenue
      FROM (
        SELECT
          DATE(payment_timestamp) AS day,
          {dimension},
          SUM(CASE WHEN payment_status = 'success' THEN amount ELSE 0 END) AS daily_revenue
        FROM payments
        WHERE DATE(payment_timestamp) >= (SELECT current_day - 7 FROM target_day)
          AND DATE(payment_timestamp) < (SELECT current_day FROM target_day)
        GROUP BY 1, 2
      )
      GROUP BY 1
    )
    SELECT
      COALESCE(c.segment, b.segment) AS segment,
      COALESCE(c.current_revenue, 0) AS current_revenue,
      COALESCE(b.baseline_revenue, 0) AS baseline_revenue,
      ROUND(COALESCE(c.current_revenue, 0) - COALESCE(b.baseline_revenue, 0), 2) AS absolute_delta,
      ROUND(((COALESCE(c.current_revenue, 0) - COALESCE(b.baseline_revenue, 0)) / NULLIF(COALESCE(b.baseline_revenue, 0), 0)) * 100, 2) AS delta_pct
    FROM current_period c
    FULL OUTER JOIN baseline_period b
      ON c.segment = b.segment
    WHERE COALESCE(b.baseline_revenue, 0) >= 3000 OR COALESCE(c.current_revenue, 0) >= 3000
    ORDER BY absolute_delta ASC
    """


def build_segment_queries(period: str = "latest"):
    dimensions = ["device_type", "country", "provider", "payment_method"]
    return {dimension: build_segment_delta_query(dimension, period=period) for dimension in dimensions}


def build_validation_query_target_cluster(period: str = "latest"):
    return f"""
    WITH target_day AS (
      {_target_day_cte(period)}
    ),
    current_stats AS (
      SELECT
        COUNT(*) AS total_payments,
        ROUND(100.0 * SUM(CASE WHEN payment_status = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2) AS current_success_rate
      FROM payments
      WHERE DATE(payment_timestamp) = (SELECT current_day FROM target_day)
        AND provider = 'razorpay'
        AND payment_method = 'upi'
        AND country = 'India'
        AND device_type = 'mobile'
    ),
    baseline_stats AS (
      SELECT AVG(success_rate) AS baseline_success_rate
      FROM (
        SELECT
          DATE(payment_timestamp) AS day,
          100.0 * SUM(CASE WHEN payment_status = 'success' THEN 1 ELSE 0 END) / COUNT(*) AS success_rate
        FROM payments
        WHERE DATE(payment_timestamp) >= (SELECT current_day - 7 FROM target_day)
          AND DATE(payment_timestamp) < (SELECT current_day FROM target_day)
          AND provider = 'razorpay'
          AND payment_method = 'upi'
          AND country = 'India'
          AND device_type = 'mobile'
        GROUP BY 1
      )
    )
    SELECT
      'razorpay' AS provider,
      'upi' AS payment_method,
      'India' AS country,
      'mobile' AS device_type,
      c.total_payments,
      c.current_success_rate,
      ROUND(COALESCE(b.baseline_success_rate, 0), 2) AS baseline_success_rate,
      ROUND(c.current_success_rate - COALESCE(b.baseline_success_rate, 0), 2) AS success_rate_delta
    FROM current_stats c
    CROSS JOIN baseline_stats b
    """


def build_validation_query_payment_success(period: str = "latest"):
    return f"""
    WITH target_day AS (
      {_target_day_cte(period)}
    ),
    current_stats AS (
      SELECT
        provider,
        payment_method,
        country,
        device_type,
        COUNT(*) AS total_payments,
        SUM(CASE WHEN payment_status = 'success' THEN 1 ELSE 0 END) AS success_count,
        ROUND(100.0 * SUM(CASE WHEN payment_status = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2) AS current_success_rate
      FROM payments
      WHERE DATE(payment_timestamp) = (SELECT current_day FROM target_day)
      GROUP BY 1, 2, 3, 4
    ),
    baseline_stats AS (
      SELECT
        provider,
        payment_method,
        country,
        device_type,
        AVG(success_rate) AS baseline_success_rate
      FROM (
        SELECT
          DATE(payment_timestamp) AS day,
          provider,
          payment_method,
          country,
          device_type,
          100.0 * SUM(CASE WHEN payment_status = 'success' THEN 1 ELSE 0 END) / COUNT(*) AS success_rate
        FROM payments
        WHERE DATE(payment_timestamp) >= (SELECT current_day - 7 FROM target_day)
          AND DATE(payment_timestamp) < (SELECT current_day FROM target_day)
        GROUP BY 1, 2, 3, 4, 5
      )
      GROUP BY 1, 2, 3, 4
    )
    SELECT
      c.provider,
      c.payment_method,
      c.country,
      c.device_type,
      c.total_payments,
      c.current_success_rate,
      ROUND(COALESCE(b.baseline_success_rate, 0), 2) AS baseline_success_rate,
      ROUND(c.current_success_rate - COALESCE(b.baseline_success_rate, 0), 2) AS success_rate_delta
    FROM current_stats c
    LEFT JOIN baseline_stats b
      ON c.provider = b.provider
      AND c.payment_method = b.payment_method
      AND c.country = b.country
      AND c.device_type = b.device_type
    WHERE c.total_payments >= 5
    ORDER BY
      CASE WHEN c.provider = 'razorpay' AND c.payment_method = 'upi' AND c.country = 'India' AND c.device_type = 'mobile' THEN 0 ELSE 1 END,
      success_rate_delta ASC,
      c.total_payments DESC
    LIMIT 20
    """


def build_validation_query_failed_payment_errors(period: str = "latest"):
    return f"""
    WITH target_day AS (
      {_target_day_cte(period)}
    )
    SELECT
      provider,
      payment_method,
      country,
      device_type,
      error_code,
      COUNT(*) AS failure_count
    FROM payments
    WHERE DATE(payment_timestamp) = (SELECT current_day FROM target_day)
      AND payment_status = 'failed'
    GROUP BY 1, 2, 3, 4, 5
    HAVING COUNT(*) >= 3
    ORDER BY
      CASE WHEN provider = 'razorpay' AND payment_method = 'upi' AND country = 'India' AND device_type = 'mobile' THEN 0 ELSE 1 END,
      failure_count DESC
    LIMIT 20
    """
