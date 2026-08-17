"""HR Multi-Agent — FastAPI router.

Multi-agent panel pipeline: session → panel → history
Three HR specialists (HR Manager, Performance Evaluator, Risk Assessor) run in parallel,
then the HR Director synthesises a final attrition risk decision via Groq LLM.

Prefix: /api/hr-multi-agent
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.session_store import Session, SessionNotFound, create_session, require_session
from applications.hr_multi_agent.services.panel_graph import AgentConfig, run_panel

router = APIRouter(prefix="/api/hr-multi-agent", tags=["HR Multi-Agent"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class SessionResponse(BaseModel):
    session_id: str

class SpecialistReportOut(BaseModel):
    role: str
    analysis: str
    recommendation: str

class PanelRequest(BaseModel):
    employee: dict[str, Any]
    llm_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    temperature: float = 0.0

class PanelResponse(BaseModel):
    hr_manager_report: SpecialistReportOut
    perf_evaluator_report: SpecialistReportOut
    risk_assessor_report: SpecialistReportOut
    final_answer: str
    risk_level: str
    timestamp: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/session", response_model=SessionResponse)
def create_panel_session():
    """Create a new session. Pass the returned session_id to /panel and /history."""
    sid = create_session()
    return {"session_id": sid}


@router.post("/{session_id}/panel", response_model=PanelResponse)
def panel(session_id: str, req: PanelRequest):
    """
    Submit an employee record to the multi-agent HR panel.

    Three specialist agents (HR Manager, Performance Evaluator, Risk Assessor) analyse
    the employee independently, then the HR Director synthesises a final risk decision.
    Returns risk_level: HIGH / MEDIUM / LOW.
    """
    session = _get_session(session_id)
    config = AgentConfig(llm_model=req.llm_model, temperature=req.temperature)
    try:
        result = run_panel(req.employee, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Panel run failed: {e}")
    entry = {
        "hr_manager_report": {
            "role": result.hr_manager_report.role,
            "analysis": result.hr_manager_report.analysis,
            "recommendation": result.hr_manager_report.recommendation,
        },
        "perf_evaluator_report": {
            "role": result.perf_evaluator_report.role,
            "analysis": result.perf_evaluator_report.analysis,
            "recommendation": result.perf_evaluator_report.recommendation,
        },
        "risk_assessor_report": {
            "role": result.risk_assessor_report.role,
            "analysis": result.risk_assessor_report.analysis,
            "recommendation": result.risk_assessor_report.recommendation,
        },
        "final_answer": result.final_answer,
        "risk_level": result.risk_level,
        "timestamp": result.timestamp,
    }
    session.panel_history.append(entry)
    return entry


@router.get("/{session_id}/history")
def get_history(session_id: str):
    """Return all panel runs for this session."""
    session = _get_session(session_id)
    return session.panel_history


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_session(session_id: str) -> Session:
    try:
        return require_session(session_id)
    except SessionNotFound:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found. Call POST /api/hr-multi-agent/session first.",
        )
