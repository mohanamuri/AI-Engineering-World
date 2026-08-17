"""HR Agent — FastAPI router.

AI agent pipeline: session → run → history
Runs three deterministic tools then synthesises an attrition risk report via Groq LLM.

Prefix: /api/hr-agent
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.session_store import Session, SessionNotFound, create_session, require_session
from applications.hr_agent.services.agent_graph import AgentConfig, run_agent

router = APIRouter(prefix="/api/hr-agent", tags=["HR Agent"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class SessionResponse(BaseModel):
    session_id: str

class AgentStepOut(BaseModel):
    tool_name: str
    tool_input: str
    tool_output: str

class RunRequest(BaseModel):
    employee: dict[str, Any]
    llm_model: str = "mixtral-8x7b-32768"
    temperature: float = 0.0

class RunResponse(BaseModel):
    steps: list[AgentStepOut]
    final_answer: str
    risk_level: str
    risk_score: int
    timestamp: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/session", response_model=SessionResponse)
def create_agent_session():
    """Create a new session. Pass the returned session_id to /run and /history."""
    sid = create_session()
    return {"session_id": sid}


@router.post("/{session_id}/run", response_model=RunResponse)
def run(session_id: str, req: RunRequest):
    """
    Submit an employee record for attrition risk assessment.

    The agent runs three deterministic tools (validate, compute attrition risk, lookup policy)
    then synthesises a structured HIGH / MEDIUM / LOW risk report via Groq LLM.
    """
    session = _get_session(session_id)
    config = AgentConfig(llm_model=req.llm_model, temperature=req.temperature)
    try:
        result = run_agent(req.employee, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent run failed: {e}")
    entry = {
        "steps": [
            {"tool_name": s.tool_name, "tool_input": s.tool_input, "tool_output": s.tool_output}
            for s in result.steps
        ],
        "final_answer": result.final_answer,
        "risk_level": result.risk_level,
        "risk_score": result.risk_score,
        "timestamp": result.timestamp,
    }
    session.agent_history.append(entry)
    return entry


@router.get("/{session_id}/history")
def get_history(session_id: str):
    """Return all agent runs for this session."""
    session = _get_session(session_id)
    return session.agent_history


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_session(session_id: str) -> Session:
    try:
        return require_session(session_id)
    except SessionNotFound:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found. Call POST /api/hr-agent/session first.",
        )
