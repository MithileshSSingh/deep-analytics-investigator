from fastapi import APIRouter, HTTPException
from app.api.schemas import InvestigateRequest, InvestigateResponse
from app.graph.workflow import run_investigation

router = APIRouter()


@router.post("/investigate", response_model=InvestigateResponse)
def investigate(request: InvestigateRequest):
    try:
        result = run_investigation(request.question)
        report = result["final_report"]
        return InvestigateResponse(
            summary=report["summary"],
            what_changed=report["what_changed"],
            top_findings=report["top_findings"],
            likely_causes=report["likely_causes"],
            next_steps=report["next_steps"],
            confidence=report["confidence"],
            trace=result["trace"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
