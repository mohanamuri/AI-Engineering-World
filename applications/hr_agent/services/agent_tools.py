"""Agent tools for the HR Analytics attrition risk agent.

Three deterministic tools run before the LLM synthesises its report:
  1. validate_employee_data — check all required fields are present and valid
  2. compute_attrition_risk — score the employee on key attrition risk factors
  3. lookup_retention_policy — return hardcoded retention intervention guidelines
"""

from __future__ import annotations

import json
from langchain_core.tools import tool


@tool
def validate_employee_data(employee_json: str) -> str:
    """Validate that an employee profile has all required fields and valid values.

    Args:
        employee_json: JSON string with employee fields.

    Returns:
        Validation summary with pass/fail for each required field.
    """
    required = [
        "Age", "Department", "JobRole", "JobSatisfaction",
        "EnvironmentSatisfaction", "WorkLifeBalance", "OverTime",
        "YearsAtCompany", "YearsSinceLastPromotion", "MonthlyIncome",
        "NumCompaniesWorked", "TotalWorkingYears",
    ]
    try:
        data = json.loads(employee_json)
    except json.JSONDecodeError:
        return "VALIDATION FAILED: Could not parse employee JSON."

    missing = [f for f in required if f not in data]
    invalid = []

    # Range checks
    try:
        if "Age" in data and not (18 <= int(data["Age"]) <= 70):
            invalid.append(f"Age={data['Age']} (expected 18-70)")
        if "JobSatisfaction" in data and int(data["JobSatisfaction"]) not in (1, 2, 3, 4):
            invalid.append(f"JobSatisfaction={data['JobSatisfaction']} (expected 1-4)")
        if "WorkLifeBalance" in data and int(data["WorkLifeBalance"]) not in (1, 2, 3, 4):
            invalid.append(f"WorkLifeBalance={data['WorkLifeBalance']} (expected 1-4)")
        if "EnvironmentSatisfaction" in data and int(data["EnvironmentSatisfaction"]) not in (1, 2, 3, 4):
            invalid.append(f"EnvironmentSatisfaction={data['EnvironmentSatisfaction']} (expected 1-4)")
    except (ValueError, TypeError):
        invalid.append("One or more numeric fields have non-numeric values.")

    if missing:
        return f"VALIDATION FAILED: Missing fields: {', '.join(missing)}"
    if invalid:
        return f"VALIDATION WARNING: Invalid values — {'; '.join(invalid)}. Profile is usable but review these fields."
    return (
        f"VALIDATION PASSED: All {len(required)} required fields present and valid. "
        f"Employee: {data.get('JobRole', 'Unknown')} in {data.get('Department', 'Unknown')}."
    )


@tool
def compute_attrition_risk(employee_json: str) -> str:
    """Score the employee's attrition risk based on key factors.

    Uses evidence-based risk factors from HR research. Each factor
    contributes a risk score; the total is normalised to 0-100.

    Args:
        employee_json: JSON string with employee fields.

    Returns:
        Risk score, risk band, and contributing factors.
    """
    try:
        data = json.loads(employee_json)
    except json.JSONDecodeError:
        return "RISK SCORING FAILED: Could not parse employee JSON."

    risk_points = 0
    factors = []

    def get_int(key: str, default: int = 0) -> int:
        try:
            return int(data.get(key, default))
        except (ValueError, TypeError):
            return default

    # OverTime (strong predictor)
    overtime = str(data.get("OverTime", "No")).strip().lower()
    if overtime in ("yes", "1", "true"):
        risk_points += 25
        factors.append("OverTime=Yes (+25 pts) — strongest individual predictor of attrition")

    # Job Satisfaction (1=low, 4=high)
    job_sat = get_int("JobSatisfaction", 3)
    if job_sat == 1:
        risk_points += 20
        factors.append(f"JobSatisfaction=1 (Very Low) (+20 pts)")
    elif job_sat == 2:
        risk_points += 10
        factors.append(f"JobSatisfaction=2 (Low) (+10 pts)")

    # Work-Life Balance (1=Bad, 4=Best)
    wlb = get_int("WorkLifeBalance", 3)
    if wlb == 1:
        risk_points += 15
        factors.append(f"WorkLifeBalance=1 (Bad) (+15 pts)")
    elif wlb == 2:
        risk_points += 7
        factors.append(f"WorkLifeBalance=2 (Poor) (+7 pts)")

    # Environment Satisfaction
    env_sat = get_int("EnvironmentSatisfaction", 3)
    if env_sat == 1:
        risk_points += 15
        factors.append(f"EnvironmentSatisfaction=1 (Very Low) (+15 pts)")
    elif env_sat == 2:
        risk_points += 7
        factors.append(f"EnvironmentSatisfaction=2 (Low) (+7 pts)")

    # Years since last promotion
    yslp = get_int("YearsSinceLastPromotion", 0)
    if yslp >= 5:
        risk_points += 15
        factors.append(f"YearsSinceLastPromotion={yslp} (≥5 years, stagnation risk) (+15 pts)")
    elif yslp >= 3:
        risk_points += 7
        factors.append(f"YearsSinceLastPromotion={yslp} (+7 pts)")

    # Number of companies worked
    ncw = get_int("NumCompaniesWorked", 1)
    if ncw >= 5:
        risk_points += 10
        factors.append(f"NumCompaniesWorked={ncw} (high job-hopping history) (+10 pts)")
    elif ncw >= 3:
        risk_points += 5
        factors.append(f"NumCompaniesWorked={ncw} (+5 pts)")

    # Clamp to 100
    risk_points = min(risk_points, 100)

    if risk_points >= 60:
        band = "HIGH"
    elif risk_points >= 35:
        band = "MEDIUM"
    else:
        band = "LOW"

    if not factors:
        factors = ["No significant risk factors identified."]

    factor_str = "\n  ".join(f"• {f}" for f in factors)
    return (
        f"ATTRITION RISK SCORE: {risk_points}/100 — {band} RISK\n\n"
        f"Contributing factors:\n  {factor_str}\n\n"
        f"Monthly Income: ${get_int('MonthlyIncome', 0):,} · "
        f"Years at Company: {get_int('YearsAtCompany', 0)} · "
        f"Total Working Years: {get_int('TotalWorkingYears', 0)}"
    )


@tool
def lookup_retention_policy(topic: str) -> str:
    """Look up HR retention intervention guidelines for a given topic.

    Args:
        topic: One of 'high_risk', 'medium_risk', 'overtime', 'promotion', 'compensation'.

    Returns:
        Relevant retention policy guidelines.
    """
    policies = {
        "high_risk": (
            "HIGH RISK RETENTION POLICY:\n"
            "• Immediate 1-on-1 retention conversation with direct manager within 5 business days\n"
            "• Career development plan review and update within 30 days\n"
            "• Compensation benchmarking against market rates\n"
            "• Consider retention bonus if top performer (performance rating 3+)\n"
            "• Review workload and overtime obligations — reduce if possible\n"
            "• Escalate to HR Business Partner if risk persists after 60 days"
        ),
        "medium_risk": (
            "MEDIUM RISK RETENTION POLICY:\n"
            "• Schedule a career development conversation within 30 days\n"
            "• Review promotion eligibility and timeline with manager\n"
            "• Assess workload balance and flexibility options\n"
            "• Ensure employee is enrolled in relevant L&D programmes\n"
            "• Monitor engagement scores in next quarterly survey"
        ),
        "overtime": (
            "OVERTIME MANAGEMENT POLICY:\n"
            "• Employees working regular overtime are 2-3x more likely to leave\n"
            "• Review and redistribute workload within the team\n"
            "• Consider additional headcount or contractor support\n"
            "• Ensure overtime compensation is market-competitive\n"
            "• Offer flexible working arrangements as an alternative"
        ),
        "promotion": (
            "PROMOTION AND CAREER GROWTH POLICY:\n"
            "• Employees with 3+ years since last promotion should be reviewed immediately\n"
            "• Create a documented career path with clear promotion criteria\n"
            "• Lateral moves and scope expansions can substitute when vertical promotions are limited\n"
            "• 6-month check-ins on development goals are mandatory for employees flagged at risk"
        ),
        "compensation": (
            "COMPENSATION RETENTION POLICY:\n"
            "• Compensation below 25th percentile of market rate significantly increases attrition risk\n"
            "• Annual salary benchmarking is required for all at-risk roles\n"
            "• Retention bonuses may be approved by the HR Director for critical talent\n"
            "• Non-monetary benefits (flexible working, L&D budget) should be highlighted"
        ),
    }
    key = topic.lower().strip()
    return policies.get(key, (
        "GENERAL RETENTION GUIDELINES:\n"
        "• Schedule regular check-ins to identify engagement issues early\n"
        "• Maintain open channels for feedback and career discussions\n"
        "• Benchmark compensation and benefits annually\n"
        "• Recognise and reward high performance consistently"
    ))
