from app.graph.workflow import run_investigation
from app.graph.nodes.generate_hypotheses_llm import _validate_hypotheses_payload


def test_generate_hypotheses_llm_falls_back_cleanly_when_disabled():
    result = run_investigation("Why did revenue drop yesterday?")
    nodes = [item["node"] for item in result["trace"]]
    messages = [item["message"] for item in result["trace"] if item["node"] == "generate_hypotheses_llm"]

    assert "generate_hypotheses_llm" in nodes
    assert any("fallback" in msg.lower() or "disabled" in msg.lower() for msg in messages)
    assert result["hypotheses"]


def test_validate_hypotheses_payload_removes_generic_when_specific_exists():
    hypotheses = _validate_hypotheses_payload(
        {
            "hypotheses": [
                {
                    "id": "h1_payment_failure",
                    "title": "Payment provider issue",
                    "reason": "Provider revenue dropped.",
                },
                {
                    "id": "h0_general_decline",
                    "title": "General weakness",
                    "reason": "Fallback.",
                },
            ]
        }
    )

    assert [item["id"] for item in hypotheses] == ["h1_payment_failure"]


def test_validate_hypotheses_payload_rejects_unknown_id():
    try:
        _validate_hypotheses_payload(
            {
                "hypotheses": [
                    {
                        "id": "h999_made_up",
                        "title": "Nope",
                        "reason": "Nope",
                    }
                ]
            }
        )
        assert False, "Expected validation error"
    except ValueError:
        pass
