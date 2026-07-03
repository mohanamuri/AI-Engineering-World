"""Structured decision report — page 3 of the loan agent workflow."""

from __future__ import annotations

import streamlit as st

from applications.loan_agent.constants import (
    NAVIGATION_SESSION_KEY,
    RUN_RESULT_SESSION_KEY,
)
from applications.loan_agent.services.agent_graph import AgentRunResult


_DECISION_META = {
    "APPROVED":       {"color": "#059669", "bg": "#dcfce7", "border": "#86efac", "icon": "✅"},
    "DECLINED":       {"color": "#dc2626", "bg": "#fee2e2", "border": "#fca5a5", "icon": "❌"},
    "MANUAL_REVIEW":  {"color": "#d97706", "bg": "#fef9c3", "border": "#fde047", "icon": "⚠️"},
    "UNKNOWN":        {"color": "#6366f1", "bg": "#eef2ff", "border": "#c7d2fe", "icon": "❓"},
}


def render() -> None:
    st.header("📄 Decision Report")
    st.caption("Structured output from the agent run. Every claim traces back to a tool result.")

    result: AgentRunResult | None = st.session_state.get(RUN_RESULT_SESSION_KEY)
    if result is None:
        with st.container(border=True):
            st.warning("No agent run yet.")
            st.button(
                "← Go to Run Agent",
                type="primary",
                on_click=lambda: st.session_state.update(
                    {NAVIGATION_SESSION_KEY: "🤖 Run Agent"}
                ),
            )
        return

    meta = _DECISION_META.get(result.decision, _DECISION_META["UNKNOWN"])

    # ---- Decision banner ------------------------------------------------
    st.markdown(
        f"""
        <div style="background:{meta['bg']};border:1px solid {meta['border']};
                    border-radius:.85rem;padding:1.25rem 1.5rem;margin-bottom:1rem;">
            <div style="font-size:2rem;">{meta['icon']}</div>
            <div style="font-size:1.5rem;font-weight:800;color:{meta['color']};
                        margin:.25rem 0 .1rem;">
                {result.decision.replace('_', ' ')}
            </div>
            <div style="font-size:.8rem;color:#64748b;">
                Evaluated by AI Agent · {result.timestamp[:10]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Applicant summary ---------------------------------------------
    app = result.application
    with st.container(border=True):
        st.markdown(f"**{app.get('applicant_name', 'Unknown')}**")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Loan type", app.get("loan_type", "—").replace(" Loan", ""))
        m2.metric("Amount", f"${app.get('loan_amount_usd', 0):,.0f}")
        m3.metric("Tenure", f"{app.get('loan_tenure_months', 0)} mo")
        m4.metric("Credit score", app.get("credit_score", "—"))
        m5.metric("Monthly income", f"${app.get('monthly_income_usd', 0):,.0f}")

    st.divider()

    # ---- Full agent reasoning ------------------------------------------
    st.subheader("Agent reasoning")
    st.markdown(result.final_answer)

    st.divider()

    # ---- Tool call summary ---------------------------------------------
    st.subheader(f"Tool calls ({len(result.steps)})")
    for step in result.steps:
        st.markdown(f"**`{step.tool_name}`**")
        st.code(step.tool_output, language="text")

    st.divider()
    col_dl, col_hist = st.columns(2)
    with col_dl:
        st.button(
            "→ Download Report",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: "⬇ Download"}
            ),
        )
    with col_hist:
        st.button(
            "→ View History",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: "📜 History"}
            ),
        )
