from app.graph.workflow import run_investigation


EXPECTED_CORE_NODE_ORDER = [
    "parse_question_llm",
    "parse_question",
    "select_route_llm",
    "resolve_metric",
    "run_baseline_queries",
    "run_segment_breakdowns",
    "generate_hypotheses_llm",
    "generate_hypotheses",
    "validate_hypotheses",
    "rank_hypotheses",
    "generate_report_llm",
    "generate_report",
]


def _trace_nodes(result):
    return [item["node"] for item in result["trace"]]


def _assert_in_relative_order(nodes, expected_nodes):
    positions = {}
    for node in expected_nodes:
        assert node in nodes, f"Missing node in trace: {node}"
        positions[node] = nodes.index(node)

    sorted_positions = [positions[node] for node in expected_nodes]
    assert sorted_positions == sorted(sorted_positions), f"Nodes out of order: {positions}"


def test_llm_fallback_trace_covers_full_decline_workflow():
    result = run_investigation("Why did revenue drop yesterday?")
    nodes = _trace_nodes(result)

    _assert_in_relative_order(nodes, EXPECTED_CORE_NODE_ORDER)

    fallback_messages = {
        item["node"]: item["message"].lower()
        for item in result["trace"]
        if item["node"] in {
            "parse_question_llm",
            "select_route_llm",
            "generate_hypotheses_llm",
            "generate_report_llm",
        }
    }

    assert any(word in fallback_messages["parse_question_llm"] for word in ["fallback", "disabled"])
    assert any(word in fallback_messages["select_route_llm"] for word in ["fallback", "disabled"])
    assert any(word in fallback_messages["generate_hypotheses_llm"] for word in ["fallback", "disabled"])
    assert any(word in fallback_messages["generate_report_llm"] for word in ["fallback", "disabled"])

    assert result["parsed_question"]["metric"] == "revenue"
    assert result["selected_route"]["name"] == "revenue_investigation"
    assert result["plan"]["route"] == "revenue_investigation"
    assert result["hypotheses"]
    assert result["validated_hypotheses"]
    assert result["ranked_hypotheses"]
    assert result["final_report"]["likely_causes"]
    assert "dropped" in result["final_report"]["summary"].lower()


def test_llm_fallback_trace_handles_non_decline_without_incident_language():
    result = run_investigation("How is revenue today?")
    nodes = _trace_nodes(result)

    assert "parse_question_llm" in nodes
    assert "select_route_llm" in nodes
    assert "generate_hypotheses_llm" in nodes
    assert "generate_report_llm" in nodes

    assert result["parsed_question"]["period"] == "today"
    assert result["parsed_question"]["investigation_type"] in {"metric_increase", "metric_change"}
    assert result["selected_route"]["name"] == "revenue_investigation"
    assert result["hypotheses"] == []
    assert result["final_report"]["likely_causes"] == []
    assert "increased" in result["final_report"]["summary"].lower()
    assert "no negative incident" in result["final_report"]["summary"].lower()


def test_llm_end_to_end_report_contract_remains_stable():
    result = run_investigation("Why did revenue drop yesterday?")
    report = result["final_report"]

    assert set(report.keys()) == {
        "summary",
        "what_changed",
        "top_findings",
        "likely_causes",
        "next_steps",
        "confidence",
    }
    assert isinstance(report["summary"], str) and report["summary"].strip()
    assert isinstance(report["what_changed"], list) and len(report["what_changed"]) >= 4
    assert isinstance(report["top_findings"], list)
    assert isinstance(report["likely_causes"], list)
    assert isinstance(report["next_steps"], list) and len(report["next_steps"]) >= 1
    assert report["confidence"] in {"high", "medium", "low"}

    for cause in report["likely_causes"]:
        assert set(cause.keys()) == {"cause", "confidence", "evidence"}
        assert cause["confidence"] in {"high", "medium", "low"}
        assert isinstance(cause["evidence"], list)
        for evidence in cause["evidence"]:
            assert isinstance(evidence, str) and evidence.strip()
