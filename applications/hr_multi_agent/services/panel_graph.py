"""LangGraph StateGraph for the HR Analytics multi-agent panel.

Graph structure:
  START → hr_manager ─────┐
        → perf_evaluator ──┤ → hr_director → END
        → risk_assessor ───┘

Three specialists run concurrently (fan-out), then the HR Director
synthesises a final attrition risk decision (fan-in).

T5 vs T6:
  T5: One agent, sequential tools, one synthesis.
  T6: Three independent LLM specialists + one director synthesis.
      Each specialist may disagree — the director resolves conflicts.
      This surface of disagreement is the key value of multi-agent systems.
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

from applications.hr_multi_agent.services.specialist_agents import (
    SpecialistReport,
    run_hr_manager,
    run_performance_evaluator,
    run_risk_assessor,
)


def _get_groq_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


class PanelState(TypedDict):
    employee: dict
    llm_model: str
    temperature: float
    hr_manager_report: SpecialistReport | None
    perf_evaluator_report: SpecialistReport | None
    risk_assessor_report: SpecialistReport | None
    final_answer: str
    risk_level: str


@dataclass
class AgentConfig:
    llm_model: str = "openai/gpt-oss-20b"
    temperature: float = 0.0


@dataclass
class PanelRunResult:
    employee: dict
    hr_manager_report: SpecialistReport
    perf_evaluator_report: SpecialistReport
    risk_assessor_report: SpecialistReport
    final_answer: str
    risk_level: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


_DIRECTOR_PROMPT = """You are the HR Director receiving independent assessments from three specialists.
Your job is to synthesise their findings into one final attrition risk decision.

When specialists agree: confirm the consensus and state the decision.
When specialists disagree: explain which concern takes priority and why.

Priority rules:
- HIGH_RISK from ANY two specialists → final decision is HIGH RISK
- HIGH_RISK from Risk Assessor alone → MEDIUM at minimum (quantitative evidence)
- All three RETAIN → LOW RISK

Output format (use exactly these labels):
RISK LEVEL: [HIGH / MEDIUM / LOW]
CONSENSUS: [UNANIMOUS / MAJORITY / SPLIT — describe the split]
DIRECTOR REASONING: [3-4 sentences explaining the final call]
PRIORITY ACTIONS:
  - [Action 1 with owner and timeframe]
  - [Action 2 with owner and timeframe]
  - [Action 3 if applicable]
"""


def _hr_manager_node(state: PanelState) -> dict:
    llm = ChatGroq(model=state["llm_model"], temperature=state["temperature"], api_key=_get_groq_api_key())
    report = run_hr_manager(state["employee"], llm)
    return {"hr_manager_report": report}


def _perf_evaluator_node(state: PanelState) -> dict:
    llm = ChatGroq(model=state["llm_model"], temperature=state["temperature"], api_key=_get_groq_api_key())
    report = run_performance_evaluator(state["employee"], llm)
    return {"perf_evaluator_report": report}


def _risk_assessor_node(state: PanelState) -> dict:
    llm = ChatGroq(model=state["llm_model"], temperature=state["temperature"], api_key=_get_groq_api_key())
    report = run_risk_assessor(state["employee"], llm)
    return {"risk_assessor_report": report}


def _director_node(state: PanelState) -> dict:
    llm = ChatGroq(model=state["llm_model"], temperature=state["temperature"], api_key=_get_groq_api_key())

    hm = state["hr_manager_report"]
    pe = state["perf_evaluator_report"]
    ra = state["risk_assessor_report"]

    panel_summary = (
        f"HR MANAGER ({hm.recommendation}):\n{hm.analysis}\n\n"
        f"PERFORMANCE EVALUATOR ({pe.recommendation}):\n{pe.analysis}\n\n"
        f"RISK ASSESSOR ({ra.recommendation}):\n{ra.analysis}"
    )

    response = llm.invoke([
        SystemMessage(content=_DIRECTOR_PROMPT),
        HumanMessage(content=(
            f"Employee profile:\n{json.dumps(state['employee'])}\n\n"
            f"Specialist reports:\n{panel_summary}\n\n"
            "Write the HR Director's final attrition risk decision:"
        )),
    ])

    final_answer = response.content.strip()
    risk_level = _extract_risk_level(final_answer)

    return {"final_answer": final_answer, "risk_level": risk_level}


def _build_graph() -> StateGraph:
    graph = StateGraph(PanelState)
    graph.add_node("hr_manager", _hr_manager_node)
    graph.add_node("perf_evaluator", _perf_evaluator_node)
    graph.add_node("risk_assessor", _risk_assessor_node)
    graph.add_node("hr_director", _director_node)

    graph.add_edge(START, "hr_manager")
    graph.add_edge(START, "perf_evaluator")
    graph.add_edge(START, "risk_assessor")

    graph.add_edge("hr_manager", "hr_director")
    graph.add_edge("perf_evaluator", "hr_director")
    graph.add_edge("risk_assessor", "hr_director")

    graph.add_edge("hr_director", END)
    return graph.compile()


_PANEL_GRAPH = _build_graph()


def run_panel(employee: dict, config: AgentConfig) -> PanelRunResult:
    initial_state: PanelState = {
        "employee": employee,
        "llm_model": config.llm_model,
        "temperature": config.temperature,
        "hr_manager_report": None,
        "perf_evaluator_report": None,
        "risk_assessor_report": None,
        "final_answer": "",
        "risk_level": "UNKNOWN",
    }
    final_state = _PANEL_GRAPH.invoke(initial_state)
    return PanelRunResult(
        employee=employee,
        hr_manager_report=final_state["hr_manager_report"],
        perf_evaluator_report=final_state["perf_evaluator_report"],
        risk_assessor_report=final_state["risk_assessor_report"],
        final_answer=final_state["final_answer"],
        risk_level=final_state["risk_level"],
    )


def _extract_risk_level(text: str) -> str:
    for line in text.splitlines():
        upper = line.strip().upper()
        if upper.startswith("RISK LEVEL:"):
            rest = upper.replace("RISK LEVEL:", "").strip()
            if "HIGH" in rest:
                return "HIGH"
            if "MEDIUM" in rest:
                return "MEDIUM"
            if "LOW" in rest:
                return "LOW"
    upper_text = text.upper()
    if "HIGH RISK" in upper_text:
        return "HIGH"
    if "MEDIUM RISK" in upper_text:
        return "MEDIUM"
    return "LOW"
