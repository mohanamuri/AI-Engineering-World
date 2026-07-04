"""History page — past agent runs."""

from __future__ import annotations
import streamlit as st
from applications.hr_agent.constants import AGENT_RUN_HISTORY_SESSION_KEY

_RISK_COLORS = {"HIGH": "#ef4444", "MEDIUM": "#f97316", "LOW": "#22c55e", "UNKNOWN": "#94a3b8"}


def render() -> None:
    st.header("📜 Run History")
    history = st.session_state.get(AGENT_RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No agent runs yet. Profile an employee and run the agent.")
        return

    st.caption(f"{len(history)} assessment(s) this session.")

    for i, result in enumerate(reversed(history), 1):
        color = _RISK_COLORS.get(result.risk_level, "#94a3b8")
        emp = result.employee
        label = f"#{len(history) - i + 1} · {emp.get('JobRole', 'Employee')} · {result.risk_level} ({result.risk_score}/100)"
        with st.expander(label, expanded=(i == 1)):
            st.markdown(result.final_answer)
