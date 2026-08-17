"""
LangGraph StateGraph for the loan eligibility multi-agent panel.

Graph structure:
  START → underwriter → fraud_detector → compliance → supervisor → END

State flows through each node. Each specialist reads the application from
state, runs its analysis, and writes its report back to state.
The supervisor node reads all three reports and writes the final decision.

Why LangGraph StateGraph here?
--------------------------------
StateGraph makes the multi-agent flow explicit and inspectable:
  - Each node is a named step visible in the execution trace.
  - State is typed (TypedDict) — no hidden mutable globals.
  - Adding a new specialist is one new node + one new edge.
  - In production, swap sequential edges for parallel Send() calls with
    no changes to node logic.

Why TypedDict for state (not a dataclass)?
-------------------------------------------
LangGraph's StateGraph requires state to be a TypedDict or a Pydantic model.
TypedDict is chosen here because it has zero overhead — it's just a regular
dict at runtime, and LangGraph handles merging/updating it between nodes.

Interview note — T5 vs T6 comparison
--------------------------------------
T5: One agent, all tools, one LLM call for synthesis.
T6: Three independent LLM calls (specialists) + one LLM call (supervisor).
    The supervisor resolves disagreements — a non-trivial task when
    Underwriter says APPROVE but Compliance says DECLINE.
    This disagreement surface is the key value of multi-agent systems.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TypedDict

import os

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from applications.loan_multi_agent.services.specialist_agents import (
    SpecialistReport,
    run_compliance_officer,
    run_fraud_detector,
    run_underwriter,
)


def _get_groq_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class PanelState(TypedDict):
    application: dict
    llm_model: str
    temperature: float
    underwriter_report: SpecialistReport | None
    fraud_report: SpecialistReport | None
    compliance_report: SpecialistReport | None
    final_answer: str
    decision: str


# ---------------------------------------------------------------------------
# Result dataclass (returned to the UI)
# ---------------------------------------------------------------------------

@dataclass
class AgentConfig:
    llm_model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.0


@dataclass
class PanelRunResult:
    application: dict
    underwriter_report: SpecialistReport
    fraud_report: SpecialistReport
    compliance_report: SpecialistReport
    final_answer: str
    decision: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Supervisor prompt
# ---------------------------------------------------------------------------

_SUPERVISOR_PROMPT = """You are the Credit Committee Chair at FinCorp Bank.
You have received independent assessments from three specialist agents.
Your job is to synthesise their findings into one final, binding decision.

When agents agree: state the consensus and confirm the decision.
When agents disagree: explain which specialist's concerns take priority and why.

A single RECOMMEND_DECLINE from Compliance always overrides other recommendations
(regulatory non-compliance cannot be overridden by financial merit).
A RECOMMEND_DECLINE from Fraud Detector overrides Underwriter approval
(fraud risk is non-negotiable).

Output format (use exactly these labels):
DECISION: [APPROVED / DECLINED / MANUAL_REVIEW]
CONSENSUS: [UNANIMOUS / MAJORITY / SPLIT — describe the split]
SUPERVISOR REASONING: [3-4 sentences explaining the final call]
CONDITIONS: [any approval conditions, or "None"]
"""


# ---------------------------------------------------------------------------
# LangGraph nodes
# ---------------------------------------------------------------------------

def _underwriter_node(state: PanelState) -> dict:
    llm = ChatGroq(model=state["llm_model"], temperature=state["temperature"], api_key=_get_groq_api_key())
    report = run_underwriter(state["application"], llm)
    return {"underwriter_report": report}


def _fraud_node(state: PanelState) -> dict:
    llm = ChatGroq(model=state["llm_model"], temperature=state["temperature"], api_key=_get_groq_api_key())
    report = run_fraud_detector(state["application"], llm)
    return {"fraud_report": report}


def _compliance_node(state: PanelState) -> dict:
    llm = ChatGroq(model=state["llm_model"], temperature=state["temperature"], api_key=_get_groq_api_key())
    report = run_compliance_officer(state["application"], llm)
    return {"compliance_report": report}


def _supervisor_node(state: PanelState) -> dict:
    llm = ChatGroq(model=state["llm_model"], temperature=state["temperature"], api_key=_get_groq_api_key())

    uw = state["underwriter_report"]
    fd = state["fraud_report"]
    co = state["compliance_report"]

    panel_summary = (
        f"UNDERWRITER ({uw.recommendation}):\n{uw.analysis}\n\n"
        f"FRAUD DETECTOR ({fd.recommendation}):\n{fd.analysis}\n\n"
        f"COMPLIANCE OFFICER ({co.recommendation}):\n{co.analysis}"
    )

    response = llm.invoke([
        SystemMessage(content=_SUPERVISOR_PROMPT),
        HumanMessage(content=(
            f"Application:\n{json.dumps(state['application'])}\n\n"
            f"Panel reports:\n{panel_summary}\n\n"
            "Write the Credit Committee's final decision:"
        )),
    ])

    final_answer = response.content.strip()
    decision = _extract_decision(final_answer)

    return {"final_answer": final_answer, "decision": decision}


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def _build_graph() -> StateGraph:
    graph = StateGraph(PanelState)
    graph.add_node("underwriter", _underwriter_node)
    graph.add_node("fraud_detector", _fraud_node)
    graph.add_node("compliance", _compliance_node)
    graph.add_node("supervisor", _supervisor_node)

    # Fan-out: all 3 specialists start simultaneously from START
    graph.add_edge(START, "underwriter")
    graph.add_edge(START, "fraud_detector")
    graph.add_edge(START, "compliance")

    # Fan-in: supervisor waits for all 3 before running
    graph.add_edge("underwriter", "supervisor")
    graph.add_edge("fraud_detector", "supervisor")
    graph.add_edge("compliance", "supervisor")

    graph.add_edge("supervisor", END)

    return graph.compile()


_PANEL_GRAPH = _build_graph()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_panel(application: dict, config: AgentConfig) -> PanelRunResult:
    """Run the full multi-agent panel on a loan application.

    Args:
        application: Dict with all application fields.
        config:      AgentConfig (model, temperature).

    Returns:
        PanelRunResult with all specialist reports and the supervisor decision.
    """
    initial_state: PanelState = {
        "application": application,
        "llm_model": config.llm_model,
        "temperature": config.temperature,
        "underwriter_report": None,
        "fraud_report": None,
        "compliance_report": None,
        "final_answer": "",
        "decision": "UNKNOWN",
    }

    final_state = _PANEL_GRAPH.invoke(initial_state)

    return PanelRunResult(
        application=application,
        underwriter_report=final_state["underwriter_report"],
        fraud_report=final_state["fraud_report"],
        compliance_report=final_state["compliance_report"],
        final_answer=final_state["final_answer"],
        decision=final_state["decision"],
    )


def _extract_decision(text: str) -> str:
    for line in text.splitlines():
        upper = line.strip().upper()
        if upper.startswith("DECISION:"):
            rest = upper.replace("DECISION:", "").strip()
            if "APPROVED" in rest:
                return "APPROVED"
            if "DECLINED" in rest:
                return "DECLINED"
            if "MANUAL" in rest or "REVIEW" in rest:
                return "MANUAL_REVIEW"
    return "UNKNOWN"
