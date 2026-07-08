"""Consensus page — shows all specialist reports side by side."""

import streamlit as st
from applications.hr_multi_agent.constants import PANEL_RUN_HISTORY_SESSION_KEY
from applications.shared.api_reference import render_api_reference


def render() -> None:
    st.header("🤝 Consensus View")
    history = st.session_state.get(PANEL_RUN_HISTORY_SESSION_KEY, [])
    if not history:
        st.info("Run the panel first.")
        return
    latest = history[-1]

    st.markdown("Compare how each specialist analysed the same employee profile.")

    col1, col2, col3 = st.columns(3)
    for col, report in [(col1, latest.hr_manager_report),
                        (col2, latest.perf_evaluator_report),
                        (col3, latest.risk_assessor_report)]:
        with col:
            with st.container(border=True):
                st.markdown(f"**{report.role}**")
                st.markdown(f"*Verdict: {report.recommendation}*")
                st.text(report.analysis[:600] + ("…" if len(report.analysis) > 600 else ""))
    render_api_reference("hr_multi_agent", "consensus")
