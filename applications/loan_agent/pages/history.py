"""History of past agent runs — page 4 of the loan agent workflow."""

from __future__ import annotations

import streamlit as st

from applications.loan_agent.constants import (
    HISTORY_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    RUN_RESULT_SESSION_KEY,
)
from applications.loan_agent.services.agent_graph import AgentRunResult

_DECISION_COLORS = {
    "APPROVED":      "#059669",
    "DECLINED":      "#dc2626",
    "MANUAL_REVIEW": "#d97706",
    "UNKNOWN":       "#6366f1",
}
_DECISION_ICONS = {
    "APPROVED": "✅", "DECLINED": "❌", "MANUAL_REVIEW": "⚠️", "UNKNOWN": "❓"
}


def render() -> None:
    st.header("📜 Decision History")
    st.caption("All loan applications evaluated in this session.")

    history: list[AgentRunResult] = st.session_state.get(HISTORY_SESSION_KEY, [])

    if not history:
        with st.container(border=True):
            st.info("No decisions yet.")
            st.button(
                "← Go to Application",
                type="primary",
                on_click=lambda: st.session_state.update(
                    {NAVIGATION_SESSION_KEY: "📋 Application"}
                ),
            )
        return

    # ---- Summary metrics ------------------------------------------------
    approved = sum(1 for r in history if r.decision == "APPROVED")
    declined = sum(1 for r in history if r.decision == "DECLINED")
    review = sum(1 for r in history if r.decision == "MANUAL_REVIEW")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total evaluated", len(history))
    m2.metric("Approved", approved)
    m3.metric("Declined", declined)
    m4.metric("Manual review", review)

    st.divider()

    # ---- Cards ----------------------------------------------------------
    for i, result in enumerate(reversed(history)):
        app = result.application
        color = _DECISION_COLORS.get(result.decision, "#6366f1")
        icon = _DECISION_ICONS.get(result.decision, "❓")

        with st.container(border=True):
            col_decision, col_details, col_action = st.columns([2, 6, 2])

            with col_decision:
                st.markdown(
                    f"<div style='font-size:1.4rem;'>{icon}</div>"
                    f"<div style='font-size:.75rem;font-weight:700;color:{color};"
                    f"text-transform:uppercase;'>{result.decision.replace('_',' ')}</div>",
                    unsafe_allow_html=True,
                )

            with col_details:
                st.markdown(f"**{app.get('applicant_name', 'Unknown')}**")
                st.caption(
                    f"{app.get('loan_type', '—')} · "
                    f"${app.get('loan_amount_usd', 0):,.0f} · "
                    f"Credit {app.get('credit_score', '—')} · "
                    f"{result.timestamp[:10]}"
                )

            with col_action:
                if st.button(
                    "View",
                    key=f"view_{i}",
                    use_container_width=True,
                ):
                    st.session_state[RUN_RESULT_SESSION_KEY] = result
                    st.session_state[NAVIGATION_SESSION_KEY] = "📄 Decision"
                    st.rerun()

    st.divider()
    st.button(
        "→ Download History",
        on_click=lambda: st.session_state.update(
            {NAVIGATION_SESSION_KEY: "⬇ Download"}
        ),
    )
