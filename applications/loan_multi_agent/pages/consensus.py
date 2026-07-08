"""Full consensus decision report — page 3 of the multi-agent workflow."""

from __future__ import annotations

import streamlit as st

from applications.loan_multi_agent.constants import (
    NAVIGATION_SESSION_KEY,
    PANEL_RESULT_SESSION_KEY,
)
from applications.loan_multi_agent.services.panel_graph import PanelRunResult
from applications.shared.api_reference import render_api_reference

_DECISION_META = {
    "APPROVED":      {"color": "#059669", "bg": "#dcfce7", "border": "#86efac", "icon": "✅"},
    "DECLINED":      {"color": "#dc2626", "bg": "#fee2e2", "border": "#fca5a5", "icon": "❌"},
    "MANUAL_REVIEW": {"color": "#d97706", "bg": "#fef9c3", "border": "#fde047", "icon": "⚠️"},
    "UNKNOWN":       {"color": "#6366f1", "bg": "#eef2ff", "border": "#c7d2fe", "icon": "❓"},
}
_REC_COLORS = {
    "RECOMMEND_APPROVE":  "#059669",
    "RECOMMEND_DECLINE":  "#dc2626",
    "RECOMMEND_REVIEW":   "#d97706",
}


def render() -> None:
    st.header("📄 Consensus Report")
    st.caption("Full panel decision: all specialist inputs and the supervisor's final ruling.")

    result: PanelRunResult | None = st.session_state.get(PANEL_RESULT_SESSION_KEY)
    if result is None:
        with st.container(border=True):
            st.warning("No panel run yet.")
            st.button("← Run the Panel", type="primary",
                on_click=lambda: st.session_state.update(
                    {NAVIGATION_SESSION_KEY: "🏛️ Run Panel"}))
        return

    meta = _DECISION_META.get(result.decision, _DECISION_META["UNKNOWN"])
    app = result.application

    # ---- Decision banner ------------------------------------------------
    st.markdown(
        f"""
        <div style="background:{meta['bg']};border:1px solid {meta['border']};
                    border-radius:.85rem;padding:1.25rem 1.5rem;margin-bottom:1rem;">
            <div style="font-size:2rem;">{meta['icon']}</div>
            <div style="font-size:1.5rem;font-weight:800;color:{meta['color']};margin:.2rem 0 .1rem;">
                {result.decision.replace('_', ' ')}
            </div>
            <div style="font-size:.8rem;color:#64748b;">
                Credit Committee · {result.timestamp[:10]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Applicant summary ---------------------------------------------
    with st.container(border=True):
        st.markdown(f"**{app.get('applicant_name', 'Unknown')}**")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Loan type", app.get("loan_type", "—").replace(" Loan", ""))
        m2.metric("Amount", f"${app.get('loan_amount_usd', 0):,.0f}")
        m3.metric("Tenure", f"{app.get('loan_tenure_months', 0)} mo")
        m4.metric("Credit score", app.get("credit_score", "—"))
        m5.metric("Monthly income", f"${app.get('monthly_income_usd', 0):,.0f}")

    st.divider()

    # ---- Panel votes ---------------------------------------------------
    st.subheader("Panel votes")
    reports = [result.underwriter_report, result.fraud_report, result.compliance_report]
    cols = st.columns(3)
    for col, report in zip(cols, reports):
        rec_color = _REC_COLORS.get(report.recommendation, "#6366f1")
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div style='font-size:1.2rem;'>{report.icon}</div>"
                    f"<div style='font-size:.85rem;font-weight:700;'>{report.agent_name}</div>"
                    f"<div style='font-size:.7rem;color:{rec_color};font-weight:700;'>"
                    f"{report.recommendation.replace('RECOMMEND_', '')}</div>",
                    unsafe_allow_html=True,
                )

    st.divider()

    # ---- Supervisor reasoning ------------------------------------------
    st.subheader("Supervisor reasoning")
    st.markdown(result.final_answer)

    st.divider()

    # ---- Specialist deep-dives ----------------------------------------
    st.subheader("Specialist reports")
    for report in reports:
        with st.expander(f"{report.icon} {report.agent_name} — {report.agent_role}", expanded=False):
            st.markdown(report.analysis)
            st.caption(f"Tools called: {', '.join(s.tool_name for s in report.tool_steps)}")
            for step in report.tool_steps:
                with st.expander(f"`{step.tool_name}`", expanded=False):
                    st.code(step.tool_output, language="text")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.button("→ Download Report", use_container_width=True,
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: "⬇ Download"}))
    with col2:
        st.button("→ View History", use_container_width=True,
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: "📜 History"}))
    render_api_reference("loan_multi_agent", "consensus")
