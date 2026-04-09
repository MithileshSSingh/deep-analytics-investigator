from app.graph.workflow import run_investigation


def test_workflow_returns_report_shape():
    result = run_investigation("Why did revenue drop yesterday?")

    assert "final_report" in result
    assert "summary" in result["final_report"]
    assert "what_changed" in result["final_report"]
    assert "top_findings" in result["final_report"]
    assert "likely_causes" in result["final_report"]
    assert "next_steps" in result["final_report"]
    assert "confidence" in result["final_report"]


def test_workflow_yesterday_drop_query_targets_actual_drop_window():
    result = run_investigation("Why did revenue drop yesterday?")
    report = result["final_report"]
    baseline = report["what_changed"]

    assert any("Revenue delta: -" in item for item in baseline)
    assert "dropped" in report["summary"].lower()
    assert report["likely_causes"][0]["evidence"]


def test_workflow_today_or_latest_respects_positive_change_language():
    result = run_investigation("How is revenue today?")
    report = result["final_report"]

    assert any("Revenue delta: 8.86%" in item for item in report["what_changed"])
    assert "increased" in report["summary"].lower()
    assert report["likely_causes"] == []
    assert "no negative incident" in report["summary"].lower()


def test_secondary_hypotheses_do_not_return_blank_evidence_strings():
    result = run_investigation("Why did revenue drop yesterday?")
    report = result["final_report"]

    for cause in report["likely_causes"]:
        for evidence in cause["evidence"]:
            assert evidence.strip()
