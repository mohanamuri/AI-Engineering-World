"""Specialist agents for the HR Analytics multi-agent panel.

Three independent specialists each assess the employee from their domain:
  - HR Manager       : Engagement, satisfaction, team dynamics, culture fit
  - Performance Evaluator : Career trajectory, promotion history, performance rating
  - Risk Assessor    : Attrition risk score, overtime, compensation, job-hopping

Each specialist makes an independent recommendation before the supervisor synthesises.
"""

from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class SpecialistReport:
    role: str
    analysis: str
    recommendation: str   # RETAIN / INTERVENE / HIGH_RISK


def run_hr_manager(employee: dict, llm) -> SpecialistReport:
    emp_json = json.dumps(employee)
    prompt = f"""You are an HR Manager assessing employee engagement and culture fit.
Analyse the employee profile below focusing on:
- Job satisfaction and environment satisfaction scores
- Work-life balance concerns
- Marital status and personal stability factors
- Years at company (loyalty signals)

Output format:
RECOMMENDATION: [RETAIN / INTERVENE / HIGH_RISK]
ANALYSIS: [3-4 sentences summarising engagement and culture concerns]
KEY CONCERNS: [bullet list of top 2-3 engagement risks]

Employee profile:
{emp_json}"""

    from langchain_core.messages import HumanMessage
    response = llm.invoke([HumanMessage(content=prompt)])
    text = response.content.strip()
    return SpecialistReport(
        role="HR Manager",
        analysis=text,
        recommendation=_extract_recommendation(text),
    )


def run_performance_evaluator(employee: dict, llm) -> SpecialistReport:
    emp_json = json.dumps(employee)
    prompt = f"""You are a Performance Evaluator assessing career trajectory and growth potential.
Analyse the employee profile below focusing on:
- Years since last promotion (stagnation risk)
- Job level vs total working years (under-levelled?)
- Number of companies worked (career mobility pattern)
- Training and development signals

Output format:
RECOMMENDATION: [RETAIN / INTERVENE / HIGH_RISK]
ANALYSIS: [3-4 sentences summarising career trajectory concerns]
KEY CONCERNS: [bullet list of top 2-3 career development risks]

Employee profile:
{emp_json}"""

    from langchain_core.messages import HumanMessage
    response = llm.invoke([HumanMessage(content=prompt)])
    text = response.content.strip()
    return SpecialistReport(
        role="Performance Evaluator",
        analysis=text,
        recommendation=_extract_recommendation(text),
    )


def run_risk_assessor(employee: dict, llm) -> SpecialistReport:
    emp_json = json.dumps(employee)
    prompt = f"""You are an HR Risk Assessor specialising in quantitative attrition risk.
Analyse the employee profile below focusing on:
- Overtime status (single strongest attrition predictor)
- Monthly income relative to job level (compensation fairness)
- Combination of low satisfaction + high overtime (burnout risk)
- Stock option level (financial retention incentive)

Output format:
RECOMMENDATION: [RETAIN / INTERVENE / HIGH_RISK]
RISK_SCORE: [0-100]
ANALYSIS: [3-4 sentences summarising quantitative risk factors]
KEY CONCERNS: [bullet list of top 2-3 risk factors]

Employee profile:
{emp_json}"""

    from langchain_core.messages import HumanMessage
    response = llm.invoke([HumanMessage(content=prompt)])
    text = response.content.strip()
    return SpecialistReport(
        role="Risk Assessor",
        analysis=text,
        recommendation=_extract_recommendation(text),
    )


def _extract_recommendation(text: str) -> str:
    for line in text.splitlines():
        upper = line.strip().upper()
        if upper.startswith("RECOMMENDATION:"):
            rest = upper.replace("RECOMMENDATION:", "").strip()
            if "HIGH_RISK" in rest or "HIGH RISK" in rest:
                return "HIGH_RISK"
            if "INTERVENE" in rest:
                return "INTERVENE"
            if "RETAIN" in rest:
                return "RETAIN"
    # Fallback scan
    upper_text = text.upper()
    if "HIGH_RISK" in upper_text or "HIGH RISK" in upper_text:
        return "HIGH_RISK"
    if "INTERVENE" in upper_text:
        return "INTERVENE"
    return "RETAIN"
