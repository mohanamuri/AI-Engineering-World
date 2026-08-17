"""
LangGraph ReAct agent for loan eligibility decisions.

Architecture:
  Phase 1 — Tools run deterministically (validate → score_risk → lookup_policy)
  Phase 2 — LLM synthesises a structured decision from all tool outputs

Why deterministic tool execution?
-----------------------------------
LangGraph's create_react_agent relies on the LLM's native function-calling
support. Local Ollama models (llama3.1) sometimes emit tool calls as raw
JSON text rather than structured function-call tokens, which breaks the
tool-dispatch loop.

Running tools unconditionally is MORE reliable for production and demos:
  - Every step is always shown — nothing is skipped.
  - Results are ground-truth numbers, not LLM guesses.
  - The LLM is used only where it adds value: synthesising language.

This also mirrors a real bank's workflow: a rules engine runs all
mandatory checks first; a credit officer then writes the decision letter.

Interview note — deterministic vs autonomous agents
-----------------------------------------------------
T5 (here) deliberately keeps control: tools always run in a fixed order.
T6 (Multi-Agent) will show true autonomy: specialist sub-agents each run
their own reasoning loop and a supervisor orchestrates consensus — no
fixed order, emergent behaviour.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from applications.loan_agent.services.agent_tools import (
    compute_risk_metrics,
    lookup_policy_rule,
    validate_application,
)


def _get_groq_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AgentStep:
    """One tool call + response in the agent's reasoning chain."""
    tool_name: str
    tool_input: str
    tool_output: str


@dataclass
class AgentRunResult:
    """Full result of one agent run."""
    application: dict
    steps: list[AgentStep] = field(default_factory=list)
    final_answer: str = ""
    decision: str = "UNKNOWN"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class AgentConfig:
    """Tunable agent parameters."""
    llm_model: str = "gemma2-9b-it"
    temperature: float = 0.0


# ---------------------------------------------------------------------------
# Synthesis prompt
# ---------------------------------------------------------------------------

_SYNTHESIS_PROMPT = """You are a FinCorp Bank loan eligibility officer.
Below are the results of three automated checks on a loan application.
Your job is to read the results and write a structured final decision.

REQUIRED OUTPUT FORMAT (use exactly these labels):
DECISION: [APPROVED / DECLINED / MANUAL_REVIEW]
REASON: [2-3 sentences citing specific numbers from the check results]
KEY METRICS:
  - Credit Score: [score] ([band])
  - DTI Ratio: [%]
  - Estimated EMI: $[amount]
CONDITIONS: [any conditions if approved, or "None"]

Decision rules:
- DECLINED if validation failed OR any auto-decline flag is present.
- MANUAL_REVIEW if DTI is 37-43% or credit score is 580-619.
- APPROVED otherwise.
"""


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_agent(application: dict, config: AgentConfig) -> AgentRunResult:
    """Run the three loan tools then synthesise a decision with the LLM.

    Phase 1 — deterministic tools (always run, always in this order):
      1. validate_application  — eligibility criteria check
      2. compute_risk_metrics  — DTI, EMI, credit band
      3. lookup_policy_rule    — auto-decline policy rules

    Phase 2 — LLM synthesis:
      Feed all tool outputs to the LLM and ask for a structured decision.

    Args:
        application: Dict with all application fields.
        config:      AgentConfig (model, temperature).

    Returns:
        AgentRunResult with step trace and structured decision.
    """
    app_json = json.dumps(application)
    steps: list[AgentStep] = []

    # ---- Phase 1: run tools ------------------------------------------------
    validation_out = validate_application.invoke({"application_json": app_json})
    steps.append(AgentStep(
        tool_name="validate_application",
        tool_input=app_json,
        tool_output=validation_out,
    ))

    risk_out = compute_risk_metrics.invoke({"application_json": app_json})
    steps.append(AgentStep(
        tool_name="compute_risk_metrics",
        tool_input=app_json,
        tool_output=risk_out,
    ))

    policy_out = lookup_policy_rule.invoke({"topic": "auto_decline"})
    steps.append(AgentStep(
        tool_name="lookup_policy_rule",
        tool_input="auto_decline",
        tool_output=policy_out,
    ))

    # ---- Phase 2: LLM synthesis -------------------------------------------
    context = (
        f"STEP 1 — Validation:\n{validation_out}\n\n"
        f"STEP 2 — Risk metrics:\n{risk_out}\n\n"
        f"STEP 3 — Policy rules:\n{policy_out}"
    )
    messages = [
        SystemMessage(content=_SYNTHESIS_PROMPT),
        HumanMessage(content=(
            f"Application under review:\n{app_json}\n\n"
            f"Automated check results:\n{context}\n\n"
            "Write your final decision using the required format:"
        )),
    ]

    llm = ChatGroq(model=config.llm_model, temperature=config.temperature, api_key=_get_groq_api_key())
    response = llm.invoke(messages)
    final_answer = response.content.strip()
    decision = _extract_decision(final_answer)

    return AgentRunResult(
        application=application,
        steps=steps,
        final_answer=final_answer,
        decision=decision,
    )


def _extract_decision(text: str) -> str:
    """Parse the DECISION: line from the LLM's final response."""
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

