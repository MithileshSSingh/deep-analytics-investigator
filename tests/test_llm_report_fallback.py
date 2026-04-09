from app.graph.workflow import run_investigation


def test_generate_report_llm_falls_back_cleanly_when_disabled():
    result = run_investigation("Why did revenue drop yesterday?")
    nodes = [item["node"] for item in result["trace"]]
    messages = [item["message"] for item in result["trace"] if item["node"] == "generate_report_llm"]

    assert "generate_report_llm" in nodes
    assert any("fallback" in msg.lower() or "disabled" in msg.lower() for msg in messages)
    assert "final_report" in result
    assert result["final_report"]["summary"]
    assert result["final_report"]["confidence"] in {"high", "medium", "low"}
