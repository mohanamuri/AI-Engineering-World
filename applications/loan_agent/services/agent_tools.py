"""
Deterministic tool functions for the loan eligibility agent.

Each tool is a pure Python function that the LangGraph ReAct agent can call.
They contain NO LLM calls — all logic is rules-based. This is intentional:

  Why deterministic tools?
  -------------------------
  The LLM is good at reasoning and language; it is bad at arithmetic and
  rule enforcement. Separating concerns gives us:
    - Auditable decisions: every number can be traced to a formula.
    - Testable tools: no mocks needed, plain unit tests suffice.
    - Agent as orchestrator: the LLM decides WHICH tool to call and in
      what order; the tools produce ground-truth facts the LLM cannot change.

  Interview note — Tool design in production agents
  ---------------------------------------------------
  In a real bank system these tools would call microservices:
  validate → KYC/AML service, score_risk → credit bureau API,
  lookup_policy → internal policy engine. The LangGraph layer stays the
  same regardless of what's behind each tool.
"""

from __future__ import annotations

import json

from langchain_core.tools import tool


# ---------------------------------------------------------------------------
# Embedded policy knowledge base (used by lookup_policy_rule)
# ---------------------------------------------------------------------------

_POLICY = {
    "min_age": 21,
    "min_income_usd": 2000,
    "min_employment_months": 12,
    "min_credit_score_standard": 620,
    "auto_decline_credit_score": 580,
    "max_dti_pct": 43,
    "auto_decline_dti_pct": 50,
    "credit_bands": {
        "Poor":       (300, 579),
        "Fair":       (580, 619),
        "Acceptable": (620, 659),
        "Good":       (660, 699),
        "Very Good":  (700, 749),
        "Excellent":  (750, 850),
    },
    "dti_bands": {
        "Excellent": (0, 28),
        "Good":      (28, 36),
        "Marginal":  (36, 43),
        "Declined":  (43, 100),
    },
    "interest_rates": {
        "620-659": "16%–18% p.a.",
        "660-699": "13%–15% p.a.",
        "700-749": "10%–12% p.a.",
        "750+":    "8%–9.5% p.a.",
    },
    "auto_decline_conditions": [
        "Credit score below 580",
        "Active bankruptcy proceedings",
        "Loan default in the last 24 months",
        "DTI exceeds 50%",
        "Undischarged insolvency",
        "Fraud flag on any credit bureau report",
    ],
}

_POLICY_TOPICS = {
    "credit": _POLICY["credit_bands"],
    "dti": _POLICY["dti_bands"],
    "rates": _POLICY["interest_rates"],
    "eligibility": {
        "min_age": _POLICY["min_age"],
        "min_income": _POLICY["min_income_usd"],
        "min_employment_months": _POLICY["min_employment_months"],
        "min_credit_score": _POLICY["min_credit_score_standard"],
        "max_dti_pct": _POLICY["max_dti_pct"],
    },
    "auto_decline": _POLICY["auto_decline_conditions"],
}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def validate_application(application_json: str) -> str:
    """Validate a loan application against FinCorp Bank's minimum eligibility criteria.

    Args:
        application_json: JSON string of the application dict with keys:
            age, monthly_income_usd, employment_months, credit_score,
            loan_amount_usd, loan_tenure_months, loan_type.

    Returns:
        Plain text summary of validation results (PASSED or list of failures).
    """
    try:
        app = json.loads(application_json)
    except json.JSONDecodeError:
        return "ERROR: Invalid JSON. Cannot validate application."

    failures = []

    if app.get("age", 0) < _POLICY["min_age"]:
        failures.append(
            f"Age {app.get('age')} < minimum {_POLICY['min_age']} years"
        )
    if app.get("monthly_income_usd", 0) < _POLICY["min_income_usd"]:
        failures.append(
            f"Monthly income ${app.get('monthly_income_usd'):,} < minimum ${_POLICY['min_income_usd']:,}"
        )
    if app.get("employment_months", 0) < _POLICY["min_employment_months"]:
        failures.append(
            f"Employment {app.get('employment_months')} months < minimum {_POLICY['min_employment_months']} months"
        )
    cs = app.get("credit_score", 0)
    if not (300 <= cs <= 850):
        failures.append(f"Credit score {cs} is outside valid range 300–850")
    if cs < _POLICY["auto_decline_credit_score"]:
        failures.append(
            f"Credit score {cs} triggers automatic decline (below {_POLICY['auto_decline_credit_score']})"
        )

    if failures:
        return "VALIDATION FAILED:\n" + "\n".join(f"  • {f}" for f in failures)
    return (
        f"VALIDATION PASSED: All minimum eligibility criteria met.\n"
        f"  • Age: {app['age']} ✓\n"
        f"  • Monthly income: ${app['monthly_income_usd']:,} ✓\n"
        f"  • Employment: {app['employment_months']} months ✓\n"
        f"  • Credit score: {app['credit_score']} ✓"
    )


@tool
def compute_risk_metrics(application_json: str) -> str:
    """Compute DTI ratio, credit score band, estimated EMI, and auto-decline flags.

    Args:
        application_json: Same JSON string as validate_application.
            Must include existing_monthly_debt_usd.

    Returns:
        Plain text risk assessment with all computed metrics.
    """
    try:
        app = json.loads(application_json)
    except json.JSONDecodeError:
        return "ERROR: Invalid JSON."

    income = float(app.get("monthly_income_usd", 0))
    existing_debt = float(app.get("existing_monthly_debt_usd", 0))
    loan_amount = float(app.get("loan_amount_usd", 0))
    tenure = int(app.get("loan_tenure_months", 12))
    credit_score = int(app.get("credit_score", 0))

    # Approximate rate based on credit score
    if credit_score >= 750:
        annual_rate = 0.085
    elif credit_score >= 700:
        annual_rate = 0.11
    elif credit_score >= 660:
        annual_rate = 0.14
    else:
        annual_rate = 0.17

    monthly_rate = annual_rate / 12
    if monthly_rate > 0 and tenure > 0:
        emi = loan_amount * monthly_rate / (1 - (1 + monthly_rate) ** -tenure)
    else:
        emi = loan_amount / tenure if tenure > 0 else 0

    total_obligations = existing_debt + emi
    dti = (total_obligations / income * 100) if income > 0 else 999

    # Credit band
    band = "Unknown"
    for name, (lo, hi) in _POLICY["credit_bands"].items():
        if lo <= credit_score <= hi:
            band = name
            break

    # DTI band
    dti_band = "Declined"
    for name, (lo, hi) in _POLICY["dti_bands"].items():
        if lo <= dti < hi:
            dti_band = name
            break

    auto_decline_flags = []
    if credit_score < _POLICY["auto_decline_credit_score"]:
        auto_decline_flags.append(f"Credit score {credit_score} below {_POLICY['auto_decline_credit_score']}")
    if dti > _POLICY["auto_decline_dti_pct"]:
        auto_decline_flags.append(f"DTI {dti:.1f}% exceeds auto-decline threshold of {_POLICY['auto_decline_dti_pct']}%")

    flag_str = (
        "  AUTO-DECLINE FLAGS: " + "; ".join(auto_decline_flags)
        if auto_decline_flags else
        "  No auto-decline flags triggered."
    )

    return (
        f"RISK ASSESSMENT:\n"
        f"  Monthly income:          ${income:>10,.0f}\n"
        f"  Existing monthly debt:   ${existing_debt:>10,.0f}\n"
        f"  Estimated EMI:           ${emi:>10,.0f}  (rate {annual_rate*100:.1f}% p.a.)\n"
        f"  Total monthly obligations: ${total_obligations:>8,.0f}\n"
        f"  DTI ratio:               {dti:>9.1f}%  [{dti_band}]\n"
        f"  Credit score:            {credit_score:>10}  [{band}]\n"
        f"  Applicable rate range:   {_POLICY['interest_rates'].get(f'{(credit_score//50)*50}-{(credit_score//50)*50+49}', 'see policy')}\n"
        f"{flag_str}"
    )


@tool
def lookup_policy_rule(topic: str) -> str:
    """Look up a specific FinCorp Bank loan policy rule by topic.

    Args:
        topic: One of: credit, dti, rates, eligibility, auto_decline

    Returns:
        Policy rules for that topic as plain text.
    """
    topic_lower = topic.lower().strip()

    # Fuzzy match
    for key in _POLICY_TOPICS:
        if key in topic_lower or topic_lower in key:
            return f"POLICY — {key.upper()}:\n{json.dumps(_POLICY_TOPICS[key], indent=2)}"

    return (
        f"Topic '{topic}' not found. Available topics: "
        + ", ".join(_POLICY_TOPICS.keys())
    )


# ---------------------------------------------------------------------------
# Exported list for agent construction
# ---------------------------------------------------------------------------

AGENT_TOOLS = [validate_application, compute_risk_metrics, lookup_policy_rule]
