"""History of past panel decisions — page 4."""

from __future__ import annotations

import streamlit as st

from applications.loan_multi_agent.constants import (
    HISTORY_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PANEL_RESULT_SESSION_KEY,
)
from applications.loan_multi_agent.services.panel_graph import PanelRunResult

_DECISION_COLORS = {
    "APPROVED": "#059669", "DECLINED": "#dc2626",
    "MANUAL_REVIEW": "#d97706", "UNKNOWN": "#6366f1",
}
_DECISION_ICONS = {
    "APPROVED": "✅", "DECLINED": "❌", "MANUAL_REVIEW": "⚠️", "UNKNOWN": "❓",
}


def render() -> None:
    st.header("📜 Decision History")
    st.caption("All applications reviewed by the credit committee in this session.")

    history: list[PanelRunResult] = st.session_state.get(HISTORY_SESSION_KEY, [])

    if not history:
        with st.container(border=True):
            st.info("No panel decisions yet.")
            st.button("← Go to Application", type="primary",
                on_click=lambda: st.session_state.update(
                    {NAVIGATION_SESSION_KEY: "📋 Application"}))
        return

    approved = sum(1 for r in history if r.decision == "APPROVED")
    declined = sum(1 for r in history if r.decision == "DECLINED")
    review   = sum(1 for r in history if r.decision == "MANUAL_REVIEW")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total reviewed", len(history))
    m2.metric("Approved", approved)
    m3.metric("Declined", declined)
    m4.metric("Manual review", review)

    st.divider()

    for i, result in enumerate(reversed(history)):
        app = result.application
        color = _DECISION_COLORS.get(result.decision, "#6366f1")
        icon  = _DECISION_ICONS.get(result.decision, "❓")
        votes = (
            f"UW:{result.underwriter_report.recommendation.replace('RECOMMEND_','')[0]} "
            f"FD:{result.fraud_report.recommendation.replace('RECOMMEND_','')[0]} "
            f"CO:{result.compliance_report.recommendation.replace('RECOMMEND_','')[0]}"
        )

        with st.container(border=True):
            col_d, col_info, col_votes, col_btn = st.columns([2, 5, 3, 2])
            with col_d:
                st.markdown(
                    f"<div style='font-size:1.3rem;'>{icon}</div>"
                    f"<div style='font-size:.7rem;font-weight:700;color:{color};'>"
                    f"{result.decision.replace('_',' ')}</div>",
                    unsafe_allow_html=True,
                )
            with col_info:
                st.markdown(f"**{app.get('applicant_name', 'Unknown')}**")
                st.caption(
                    f"{app.get('loan_type','—')} · ${app.get('loan_amount_usd',0):,.0f} · "
                    f"Score {app.get('credit_score','—')} · {result.timestamp[:10]}"
                )
            with col_votes:
                st.caption(f"Votes: {votes}")
            with col_btn:
                if st.button("View", key=f"view_{i}", use_container_width=True):
                    st.session_state[PANEL_RESULT_SESSION_KEY] = result
                    st.session_state[NAVIGATION_SESSION_KEY] = "📄 Consensus"
                    st.rerun()

    st.divider()
    st.button("→ Download History",
        on_click=lambda: st.session_state.update(
            {NAVIGATION_SESSION_KEY: "⬇ Download"}))
