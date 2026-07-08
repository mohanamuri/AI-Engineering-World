"""Loan Multi-Agent — FastAPI router.

Multi-agent panel pipeline: session → panel → history
Three specialists (Underwriter, Fraud Detector, Compliance) run in parallel,
then a Supervisor synthesises the final decision via Groq LLM.

Prefix: /api/loan-multi-agent
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.session_store import Session, SessionNotFound, create_session, require_session
from applications.loan_multi_agent.services.panel_graph import AgentConfig, run_panel

router = APIRouter(prefix="/api/loan-multi-agent", tags=["Loan Multi-Agent"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class SessionResponse(BaseModel):
    session_id: str

class SpecialistReportOut(BaseModel):
    agent_name: str
    agent_role: str
    analysis: str
    recommendation: str

class PanelRequest(BaseModel):
    application: dict[str, Any]
    llm_model: str = "llama-3.1-8b-instant"
    temperature: float = 0.0

class PanelResponse(BaseModel):
    underwriter_report: SpecialistReportOut
    fraud_report: SpecialistReportOut
    compliance_report: SpecialistReportOut
    final_answer: str
    decision: str
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
    Submit a loan application to the multi-agent panel.

    Three specialist agents (Underwriter, Fraud Detector, Compliance Officer) analyse
    the application independently, then the Supervisor synthesises a final decision.
    Returns APPROVED / DECLINED / MANUAL_REVIEW.
    """
    session = _get_session(session_id)
    config = AgentConfig(llm_model=req.llm_model, temperature=req.temperature)
    try:
        result = run_panel(req.application, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Panel run failed: {e}")
    entry = {
        "underwriter_report": {
            "agent_name": result.underwriter_report.agent_name,
            "agent_role": result.underwriter_report.agent_role,
            "analysis": result.underwriter_report.analysis,
            "recommendation": result.underwriter_report.recommendation,
        },
        "fraud_report": {
            "agent_name": result.fraud_report.agent_name,
            "agent_role": result.fraud_report.agent_role,
            "analysis": result.fraud_report.analysis,
            "recommendation": result.fraud_report.recommendation,
        },
        "compliance_report": {
            "agent_name": result.compliance_report.agent_name,
            "agent_role": result.compliance_report.agent_role,
            "analysis": result.compliance_report.analysis,
            "recommendation": result.compliance_report.recommendation,
        },
        "final_answer": result.final_answer,
        "decision": result.decision,
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
            detail=f"Session '{session_id}' not found. Call POST /api/loan-multi-agent/session first.",
        )
