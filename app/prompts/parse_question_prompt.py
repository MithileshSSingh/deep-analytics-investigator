from textwrap import dedent


def build_parse_question_prompt(question: str) -> str:
    return dedent(
        f"""
        You are parsing an analytics investigation question into a strict JSON object.

        Allowed metrics:
        - revenue

        Allowed routes:
        - revenue_investigation

        Allowed periods:
        - latest
        - today
        - yesterday

        Allowed investigation types:
        - metric_drop
        - metric_increase
        - metric_change

        Allowed dimensions:
        - device_type
        - country
        - provider
        - payment_method

        Return JSON only with this shape:
        {{
          "metric": "revenue",
          "route_candidates": ["revenue_investigation"],
          "period": "latest|today|yesterday",
          "comparison_period": "previous_7_days_avg",
          "dimensions_to_check": ["device_type", "country", "provider", "payment_method"],
          "filters": {{}},
          "investigation_type": "metric_drop|metric_increase|metric_change",
          "needs_clarification": false,
          "clarification_question": null,
          "confidence": "low|medium|high"
        }}

        User question:
        {question}
        """.strip()
    )
