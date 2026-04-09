from typing import Any, Dict, List

from app.models.evidence import EvidenceArtifact
from app.services.report_formatter import format_money, format_pct, safe_num


def build_baseline_artifact(baseline_results: Dict[str, Any], route: str = "revenue_investigation") -> EvidenceArtifact:
    delta_pct = safe_num(baseline_results.get("delta_pct"), 0)
    direction = "drop" if delta_pct < 0 else "increase" if delta_pct > 0 else "flat"
    return {
        "artifact_id": "baseline_revenue",
        "artifact_type": "baseline_change",
        "route": route,
        "query_name": "revenue_baseline",
        "title": "Baseline revenue movement",
        "summary": (
            f"Revenue {direction}ed to {format_money(baseline_results.get('current_value', 0))} "
            f"versus baseline {format_money(baseline_results.get('baseline_value', 0))} "
            f"({format_pct(delta_pct)})."
        ) if direction != "flat" else (
            f"Revenue was flat at {format_money(baseline_results.get('current_value', 0))} "
            f"versus baseline {format_money(baseline_results.get('baseline_value', 0))}."
        ),
        "severity": "high" if abs(delta_pct) >= 10 else "medium" if abs(delta_pct) >= 5 else "low",
        "evidence": [],
        "metadata": baseline_results,
    }


def build_segment_artifacts(segment_results: List[Dict[str, Any]], route: str = "revenue_investigation") -> List[EvidenceArtifact]:
    artifacts: List[EvidenceArtifact] = []
    for block in segment_results:
        dimension = block.get("dimension", "unknown")
        rows = block.get("rows", [])
        for idx, row in enumerate(rows[:3], start=1):
            delta_pct = safe_num(row.get("delta_pct"), 0)
            segment = row.get("segment", "unknown")
            artifacts.append({
                "artifact_id": f"segment_{dimension}_{idx}",
                "artifact_type": "segment_anomaly",
                "route": route,
                "query_name": "segment_delta",
                "dimension": dimension,
                "title": f"{dimension} anomaly: {segment}",
                "summary": (
                    f"{dimension}={segment} moved to {format_money(row.get('current_revenue', 0))} "
                    f"from {format_money(row.get('baseline_revenue', 0))} ({format_pct(delta_pct)})."
                ),
                "severity": "high" if abs(delta_pct) >= 20 else "medium" if abs(delta_pct) >= 8 else "low",
                "evidence": [],
                "metadata": row,
            })
    return artifacts


def build_evidence_artifacts(baseline_results: Dict[str, Any], segment_results: List[Dict[str, Any]], route: str = "revenue_investigation") -> List[EvidenceArtifact]:
    return [build_baseline_artifact(baseline_results, route=route), *build_segment_artifacts(segment_results, route=route)]
