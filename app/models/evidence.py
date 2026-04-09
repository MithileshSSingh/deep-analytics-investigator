from typing import Any, Dict, List, TypedDict


class EvidenceArtifact(TypedDict, total=False):
    artifact_id: str
    artifact_type: str
    route: str
    query_name: str
    dimension: str
    title: str
    summary: str
    severity: str
    evidence: List[str]
    metadata: Dict[str, Any]
