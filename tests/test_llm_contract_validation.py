from app.graph.nodes.parse_question_llm import _validate_parsed_question
from app.graph.nodes.generate_report_llm import _validate_report_shape


def test_validate_parsed_question_normalizes_valid_llm_shape():
    parsed = _validate_parsed_question(
        {
            "metric": "revenue",
            "route_candidates": ["revenue_investigation", "junk_route"],
            "period": "yesterday",
            "comparison_period": "previous_7_days_avg",
            "dimensions_to_check": ["provider", "payment_method", "noise"],
            "filters": {},
            "investigation_type": "metric_drop",
            "needs_clarification": False,
            "clarification_question": None,
            "confidence": "high",
        }
    )

    assert parsed["metric"] == "revenue"
    assert parsed["route_candidates"] == ["revenue_investigation"]
    assert parsed["dimensions_to_check"] == ["provider", "payment_method"]
    assert parsed["confidence"] == "high"


def test_validate_parsed_question_rejects_invalid_metric():
    try:
        _validate_parsed_question(
            {
                "metric": "orders",
                "period": "yesterday",
                "comparison_period": "previous_7_days_avg",
                "dimensions_to_check": ["provider"],
                "filters": {},
                "investigation_type": "metric_drop",
            }
        )
        assert False, "Expected validation error"
    except ValueError:
        pass


def test_validate_report_shape_normalizes_and_limits_output():
    report = _validate_report_shape(
        {
            "summary": " Revenue dropped sharply. ",
            "what_changed": ["a", "b", "c", "d", "e", "f", "g"],
            "top_findings": ["one", "two", "three", "four", "five", "six"],
            "likely_causes": [
                {
                    "cause": "Payment provider failure",
                    "confidence": "HIGH",
                    "evidence": [" x ", "", "y", "z", "q", "r"],
                }
            ],
            "next_steps": ["n1", "n2", "n3", "n4", "n5", "n6"],
            "confidence": "medium",
        }
    )

    assert report["summary"] == "Revenue dropped sharply."
    assert len(report["what_changed"]) == 6
    assert len(report["top_findings"]) == 5
    assert report["likely_causes"][0]["confidence"] == "high"
    assert report["likely_causes"][0]["evidence"] == ["x", "y", "z", "q", "r"]
    assert len(report["next_steps"]) == 5


def test_validate_report_shape_rejects_missing_summary():
    try:
        _validate_report_shape(
            {
                "what_changed": [],
                "top_findings": [],
                "likely_causes": [],
                "next_steps": [],
                "confidence": "low",
            }
        )
        assert False, "Expected validation error"
    except ValueError:
        pass
