from app.graph.workflow import run_investigation


def test_parse_question_llm_falls_back_cleanly_when_disabled():
    result = run_investigation("Why did revenue drop yesterday?")
    nodes = [item["node"] for item in result["trace"]]
    messages = [item["message"] for item in result["trace"] if item["node"] == "parse_question_llm"]

    assert "parse_question_llm" in nodes
    assert any("fallback" in msg.lower() or "disabled" in msg.lower() for msg in messages)
    assert result["parsed_question"]["metric"] == "revenue"
    assert result["parsed_question"]["period"] == "yesterday"
