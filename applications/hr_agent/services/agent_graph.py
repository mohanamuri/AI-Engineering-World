"""LangGraph-style agent for HR attrition risk assessment.

Phase 1: Three deterministic tools always run in order:
  1. validate_employee_data  — field presence and value validation
  2. compute_attrition_risk  — evidence-based risk scoring (0-100)
  3. lookup_retention_policy — HR retention intervention guidelines

Phase 2: LLM synthesises a structured attrition risk report.

This mirrors real HR workflows: automated rules engine first,
then an HR Business Partner writes the narrative recommendation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from applications.hr_agent.services.agent_tools import (
    validate_employee_data,
    compute_attrition_risk,
    lookup_retention_policy,
)


def _get_groq_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


@dataclass
class AgentStep:
    tool_name: str
    tool_input: str
    tool_output: str


@dataclass
class AgentRunResult:
    employee: dict
    steps: list[AgentStep] = field(default_factory=list)
    final_answer: str = ""
    risk_level: str = "UNKNOWN"
    risk_score: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AgentConfig:
    llm_model: str = "gemma2-9b-it"
    temperature: float = 0.0


_SYNTHESIS_PROMPT = """You are an HR Business Partner conducting an attrition risk assessment.
You have received automated check results for an employee. Write a structured risk report.

REQUIRED OUTPUT FORMAT (use exactly these labels):
RISK LEVEL: [HIGH / MEDIUM / LOW]
RISK SUMMARY: [2-3 sentences summarising the key risk factors from the check results]
TOP RISK FACTORS:
  - [Factor 1 and its impact]
  - [Factor 2 and its impact]
  - [Factor 3 if applicable]
RECOMMENDED INTERVENTIONS:
  - [Specific action 1 with timeframe]
  - [Specific action 2 with timeframe]
  - [Specific action 3 if applicable]
PRIORITY: [URGENT (act within 5 days) / HIGH (act within 30 days) / MONITOR (next quarterly review)]

Be specific, actionable, and base everything on the automated check results provided.
"""


def run_agent(employee: dict, config: AgentConfig) -> AgentRunResult:
    emp_json = json.dumps(employee)
    steps: list[AgentStep] = []

    # Phase 1: deterministic tools
    val_out = validate_employee_data.invoke({"employee_json": emp_json})
    steps.append(AgentStep("validate_employee_data", emp_json, val_out))

    risk_out = compute_attrition_risk.invoke({"employee_json": emp_json})
    steps.append(AgentStep("compute_attrition_risk", emp_json, risk_out))

    # Determine which policy to look up based on risk score
    policy_topic = "high_risk" if "HIGH RISK" in risk_out else "medium_risk" if "MEDIUM RISK" in risk_out else "general"
    policy_out = lookup_retention_policy.invoke({"topic": policy_topic})
    steps.append(AgentStep("lookup_retention_policy", policy_topic, policy_out))

    # Phase 2: LLM synthesis
    context = (
        f"STEP 1 — Validation:\n{val_out}\n\n"
        f"STEP 2 — Attrition Risk Scoring:\n{risk_out}\n\n"
        f"STEP 3 — Retention Policy:\n{policy_out}"
    )
    messages = [
        SystemMessage(content=_SYNTHESIS_PROMPT),
        HumanMessage(content=(
            f"Employee profile:\n{emp_json}\n\n"
            f"Automated check results:\n{context}\n\n"
            "Write the attrition risk report:"
        )),
    ]

    llm = ChatGroq(model=config.llm_model, temperature=config.temperature, api_key=_get_groq_api_key())
    response = llm.invoke(messages)
    final_answer = response.content.strip()

    risk_level = _extract_risk_level(final_answer)
    risk_score = _extract_score(risk_out)

    return AgentRunResult(
        employee=employee,
        steps=steps,
        final_answer=final_answer,
        risk_level=risk_level,
        risk_score=risk_score,
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
    # Fallback: scan body
    upper_text = text.upper()
    if "HIGH RISK" in upper_text:
        return "HIGH"
    if "MEDIUM RISK" in upper_text:
        return "MEDIUM"
    return "LOW"


def _extract_score(risk_output: str) -> int:
    import re
    match = re.search(r"SCORE:\s*(\d+)/100", risk_output)
    if match:
        return int(match.group(1))
    return 0
