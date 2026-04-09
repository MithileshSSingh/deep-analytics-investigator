from typing import Any, Dict, List
from pydantic import BaseModel, Field


class InvestigateRequest(BaseModel):
    question: str = Field(..., min_length=3)


class LikelyCause(BaseModel):
    cause: str
    confidence: str
    evidence: List[str] = []


class InvestigateResponse(BaseModel):
    summary: str
    what_changed: List[str]
    top_findings: List[str]
    likely_causes: List[LikelyCause]
    next_steps: List[str]
    confidence: str
    trace: List[Dict[str, Any]]
