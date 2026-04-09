from app.graph.workflow import run_investigation
from app.registries.route_registry import ROUTE_REGISTRY
from app.registries.query_family_registry import QUERY_FAMILY_REGISTRY
from app.registries.schema_registry import SCHEMA_REGISTRY


def test_v2_registries_exist_for_revenue_route():
    assert "revenue_investigation" in ROUTE_REGISTRY
    assert "revenue_baseline" in QUERY_FAMILY_REGISTRY
    assert "segment_delta" in QUERY_FAMILY_REGISTRY
    assert "payments" in SCHEMA_REGISTRY


def test_workflow_emits_selected_route_and_evidence_artifacts():
    result = run_investigation("Why did revenue drop yesterday?")

    assert result["selected_route"]["name"] == "revenue_investigation"
    assert "plan" in result
    assert "evidence_artifacts" in result
    assert len(result["evidence_artifacts"]) >= 1
    assert any(artifact["artifact_type"] == "baseline_change" for artifact in result["evidence_artifacts"])
    assert any(artifact["artifact_type"] == "segment_anomaly" for artifact in result["evidence_artifacts"])
