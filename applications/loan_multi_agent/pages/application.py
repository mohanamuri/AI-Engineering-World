"""Loan application form — page 1 of the multi-agent workflow."""

from __future__ import annotations

import streamlit as st

from applications.loan_multi_agent.constants import (
    APPLICATION_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
)
from components.tier_guide import render_tier_guide

_SAMPLES = {
    "Strong applicant": {
        "applicant_name": "Sarah Mitchell",
        "age": 34,
        "employment_status": "Salaried",
        "employment_months": 48,
        "monthly_income_usd": 8500,
        "existing_monthly_debt_usd": 450,
        "credit_score": 740,
        "loan_type": "Personal Loan",
        "loan_amount_usd": 15000,
        "loan_tenure_months": 36,
    },
    "Borderline applicant": {
        "applicant_name": "James Okafor",
        "age": 27,
        "employment_status": "Salaried",
        "employment_months": 14,
        "monthly_income_usd": 3800,
        "existing_monthly_debt_usd": 800,
        "credit_score": 638,
        "loan_type": "Auto Loan",
        "loan_amount_usd": 18000,
        "loan_tenure_months": 60,
    },
    "High-risk applicant": {
        "applicant_name": "Priya Sharma",
        "age": 23,
        "employment_status": "Self-employed",
        "employment_months": 8,
        "monthly_income_usd": 2200,
        "existing_monthly_debt_usd": 700,
        "credit_score": 555,
        "loan_type": "Personal Loan",
        "loan_amount_usd": 25000,
        "loan_tenure_months": 48,
    },
}

_LOAN_TYPES = ["Personal Loan", "Home Improvement Loan", "Auto Loan", "Small Business Loan", "Education Loan"]
_EMPLOYMENT_TYPES = ["Salaried", "Self-employed", "Retired"]


def render() -> None:
    st.header("📋 Loan Application")
    render_tier_guide("loan_multi_agent")
    st.caption(
        "The application will be reviewed independently by three specialist agents: "
        "Underwriter, Fraud Detector, and Compliance Officer."
    )

    with st.expander("💡 Load a sample application", expanded=True):
        cols = st.columns(3)
        for i, (label, data) in enumerate(_SAMPLES.items()):
            with cols[i]:
                if st.button(label, use_container_width=True, key=f"sample_{i}"):
                    st.session_state[APPLICATION_SESSION_KEY] = data.copy()
                    st.rerun()

    st.divider()
    saved: dict = st.session_state.get(APPLICATION_SESSION_KEY, {})

    with st.form("mas_application_form"):
        st.subheader("Applicant details")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name", value=saved.get("applicant_name", ""))
            age = st.number_input("Age", min_value=18, max_value=80, value=int(saved.get("age", 30)))
            employment = st.selectbox("Employment status", _EMPLOYMENT_TYPES,
                index=_EMPLOYMENT_TYPES.index(saved.get("employment_status", "Salaried")))
            emp_months = st.number_input("Months of employment", min_value=0, max_value=600,
                value=int(saved.get("employment_months", 24)))
        with c2:
            income = st.number_input("Monthly income (USD)", min_value=0, max_value=500_000,
                value=int(saved.get("monthly_income_usd", 5000)), step=100)
            debt = st.number_input("Existing monthly debt (USD)", min_value=0, max_value=50_000,
                value=int(saved.get("existing_monthly_debt_usd", 0)), step=50)
            credit = st.number_input("Credit score", min_value=300, max_value=850,
                value=int(saved.get("credit_score", 700)))

        st.subheader("Loan details")
        c3, c4 = st.columns(2)
        with c3:
            loan_type = st.selectbox("Loan type", _LOAN_TYPES,
                index=_LOAN_TYPES.index(saved.get("loan_type", "Personal Loan")))
            amount = st.number_input("Loan amount (USD)", min_value=1000, max_value=500_000,
                value=int(saved.get("loan_amount_usd", 10000)), step=500)
        with c4:
            tenure = st.number_input("Tenure (months)", min_value=12, max_value=180,
                value=int(saved.get("loan_tenure_months", 36)), step=12)

        submitted = st.form_submit_button("Save application", use_container_width=True, type="primary")

    if submitted:
        st.session_state[APPLICATION_SESSION_KEY] = {
            "applicant_name": name, "age": age,
            "employment_status": employment, "employment_months": emp_months,
            "monthly_income_usd": income, "existing_monthly_debt_usd": debt,
            "credit_score": credit, "loan_type": loan_type,
            "loan_amount_usd": amount, "loan_tenure_months": tenure,
        }
        st.success("Application saved. Go to **Run Panel** to convene the committee.")

    if st.session_state.get(APPLICATION_SESSION_KEY):
        st.button(
            "→ Run Panel",
            type="primary",
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: "🏛️ Run Panel"}
            ),
        )
