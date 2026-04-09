from app.graph.workflow import run_investigation
from app.graph.nodes.select_route_llm import _validate_route_payload


def test_select_route_llm_falls_back_cleanly_when_disabled():
    result = run_investigation("Why did revenue drop yesterday?")
    nodes = [item["node"] for item in result["trace"]]
    messages = [item["message"] for item in result["trace"] if item["node"] == "select_route_llm"]

    assert "select_route_llm" in nodes
    assert any("fallback" in msg.lower() or "disabled" in msg.lower() for msg in messages)
    assert result["selected_route"]["name"] == "revenue_investigation"
    assert result["plan"]["route"] == "revenue_investigation"


def test_validate_route_payload_accepts_supported_route():
    result = _validate_route_payload(
        {
            "route_name": "revenue_investigation",
            "reason": "Matches revenue metric and drop investigation type.",
            "confidence": "high",
        }
    )

    assert result["route_name"] == "revenue_investigation"
    assert result["confidence"] == "high"


def test_validate_route_payload_rejects_unknown_route():
    try:
        _validate_route_payload(
            {
                "route_name": "made_up_route",
                "reason": "Nope",
                "confidence": "medium",
            }
        )
        assert False, "Expected validation error"
    except ValueError:
        pass
