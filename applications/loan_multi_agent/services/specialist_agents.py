"""
Three specialist agents for the loan eligibility panel.

Each specialist has a distinct role, persona, and analytical lens:

  Underwriter      — financial risk: DTI, EMI affordability, income stability
  Fraud Detector   — anomaly risk: unusual income/loan ratios, employment flags
  Compliance Officer — regulatory risk: policy rules, auto-decline conditions

Each agent:
  1. Runs its relevant tools (deterministic, same tools as T5)
  2. Gets an LLM synthesis through its own specialized prompt
  3. Returns a SpecialistReport with a clear recommendation

Why three specialists instead of one?
----------------------------------------
Each agent looks at the same application through a completely different lens.
A strong credit score satisfies the Underwriter but a suspicious income-to-loan
ratio may still trigger the Fraud Detector. Separating concerns means:
  - Each agent is focused and auditable.
  - Disagreements are surfaced explicitly (Underwriter says APPROVE but
    Compliance says DECLINE because of a policy rule).
  - The Supervisor's job is to resolve those disagreements — not to do
    the original analysis.

This mirrors real bank committees: credit risk, fraud, and compliance teams
each file independent reports; a credit committee chair makes the final call.

Interview note — parallel vs sequential execution
---------------------------------------------------
In production these three agents would run in parallel (LangGraph's Send API
or async) since they are fully independent. Here they run sequentially to
keep the LangGraph graph simple and the UI output deterministic.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from applications.loan_agent.services.agent_tools import (
    compute_risk_metrics,
    lookup_policy_rule,
    validate_application,
)


# ---------------------------------------------------------------------------
# Shared data structure
# ---------------------------------------------------------------------------

@dataclass
class AgentStep:
    tool_name: str
    tool_input: str
    tool_output: str


@dataclass
class SpecialistReport:
    agent_name: str
    agent_role: str
    icon: str
    tool_steps: list[AgentStep]
    analysis: str
    recommendation: str   # RECOMMEND_APPROVE / RECOMMEND_DECLINE / RECOMMEND_REVIEW


# ---------------------------------------------------------------------------
# Underwriter Agent
# Lens: financial affordability — DTI, EMI, income-to-loan ratio
# ---------------------------------------------------------------------------

_UNDERWRITER_PROMPT = """You are the Underwriter at FinCorp Bank.
Your sole focus is financial affordability. Read the risk metrics and decide
whether this applicant can comfortably repay the loan.

Evaluate:
  • Is the DTI within policy limits?
  • Is the estimated EMI affordable relative to income?
  • Is the loan amount proportionate to monthly income?

Output format (use exactly these labels):
RECOMMENDATION: [RECOMMEND_APPROVE / RECOMMEND_DECLINE / RECOMMEND_REVIEW]
FINANCIAL ANALYSIS: [3-4 sentences with specific numbers]
CONCERNS: [list any concerns, or "None"]
"""


def run_underwriter(application: dict, llm: ChatOllama) -> SpecialistReport:
    app_json = json.dumps(application)
    steps = []

    risk_out = compute_risk_metrics.invoke({"application_json": app_json})
    steps.append(AgentStep("compute_risk_metrics", app_json, risk_out))

    response = llm.invoke([
        SystemMessage(content=_UNDERWRITER_PROMPT),
        HumanMessage(content=(
            f"Application:\n{app_json}\n\n"
            f"Risk metrics:\n{risk_out}\n\n"
            "Write your underwriting assessment:"
        )),
    ])

    analysis = response.content.strip()
    recommendation = _extract_recommendation(analysis)

    return SpecialistReport(
        agent_name="Underwriter",
        agent_role="Financial affordability",
        icon="💼",
        tool_steps=steps,
        analysis=analysis,
        recommendation=recommendation,
    )


# ---------------------------------------------------------------------------
# Fraud Detector Agent
# Lens: anomaly detection — unusual patterns, employment flags, income ratios
# ---------------------------------------------------------------------------

_FRAUD_PROMPT = """You are the Fraud & Risk Analyst at FinCorp Bank.
Your job is to identify anomalies and red flags in the application.

Look for:
  • Income vs loan amount ratio (is the loan disproportionately large?)
  • Employment duration vs claimed income level (does it add up?)
  • Age vs employment months (is the timeline plausible?)
  • Existing debt vs income (signs of debt spiral?)

Output format (use exactly these labels):
RECOMMENDATION: [RECOMMEND_APPROVE / RECOMMEND_DECLINE / RECOMMEND_REVIEW]
RISK LEVEL: [LOW / MEDIUM / HIGH]
ANOMALY FINDINGS: [list specific findings, or "No anomalies detected"]
"""


def run_fraud_detector(application: dict, llm: ChatOllama) -> SpecialistReport:
    app_json = json.dumps(application)
    steps = []

    # Validate first to get field-level data
    validation_out = validate_application.invoke({"application_json": app_json})
    steps.append(AgentStep("validate_application", app_json, validation_out))

    # Also get risk metrics for ratio analysis
    risk_out = compute_risk_metrics.invoke({"application_json": app_json})
    steps.append(AgentStep("compute_risk_metrics", app_json, risk_out))

    response = llm.invoke([
        SystemMessage(content=_FRAUD_PROMPT),
        HumanMessage(content=(
            f"Application:\n{app_json}\n\n"
            f"Validation results:\n{validation_out}\n\n"
            f"Risk metrics:\n{risk_out}\n\n"
            "Write your fraud and anomaly assessment:"
        )),
    ])

    analysis = response.content.strip()
    recommendation = _extract_recommendation(analysis)

    return SpecialistReport(
        agent_name="Fraud Detector",
        agent_role="Anomaly & fraud detection",
        icon="🔎",
        tool_steps=steps,
        analysis=analysis,
        recommendation=recommendation,
    )


# ---------------------------------------------------------------------------
# Compliance Officer Agent
# Lens: regulatory and policy compliance
# ---------------------------------------------------------------------------

_COMPLIANCE_PROMPT = """You are the Compliance Officer at FinCorp Bank.
Your job is to verify that this loan application meets all regulatory and
internal policy requirements, including ECOA, FHA, and FinCorp's own policies.

Check:
  • All minimum eligibility criteria from policy
  • Auto-decline conditions (credit score, DTI thresholds)
  • Documentation requirements completeness
  • Any borderline conditions requiring additional review

Output format (use exactly these labels):
RECOMMENDATION: [RECOMMEND_APPROVE / RECOMMEND_DECLINE / RECOMMEND_REVIEW]
COMPLIANCE STATUS: [COMPLIANT / NON_COMPLIANT / BORDERLINE]
POLICY FINDINGS: [list each policy check result]
"""


def run_compliance_officer(application: dict, llm: ChatOllama) -> SpecialistReport:
    app_json = json.dumps(application)
    steps = []

    validation_out = validate_application.invoke({"application_json": app_json})
    steps.append(AgentStep("validate_application", app_json, validation_out))

    auto_decline_policy = lookup_policy_rule.invoke({"topic": "auto_decline"})
    steps.append(AgentStep("lookup_policy_rule", "auto_decline", auto_decline_policy))

    eligibility_policy = lookup_policy_rule.invoke({"topic": "eligibility"})
    steps.append(AgentStep("lookup_policy_rule", "eligibility", eligibility_policy))

    response = llm.invoke([
        SystemMessage(content=_COMPLIANCE_PROMPT),
        HumanMessage(content=(
            f"Application:\n{app_json}\n\n"
            f"Validation:\n{validation_out}\n\n"
            f"Auto-decline policy:\n{auto_decline_policy}\n\n"
            f"Eligibility policy:\n{eligibility_policy}\n\n"
            "Write your compliance assessment:"
        )),
    ])

    analysis = response.content.strip()
    recommendation = _extract_recommendation(analysis)

    return SpecialistReport(
        agent_name="Compliance Officer",
        agent_role="Policy & regulatory compliance",
        icon="⚖️",
        tool_steps=steps,
        analysis=analysis,
        recommendation=recommendation,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_recommendation(text: str) -> str:
    for line in text.splitlines():
        upper = line.strip().upper()
        if upper.startswith("RECOMMENDATION:"):
            rest = upper.replace("RECOMMENDATION:", "").strip()
            if "DECLINE" in rest:
                return "RECOMMEND_DECLINE"
            if "REVIEW" in rest:
                return "RECOMMEND_REVIEW"
            if "APPROVE" in rest:
                return "RECOMMEND_APPROVE"
    return "RECOMMEND_REVIEW"
