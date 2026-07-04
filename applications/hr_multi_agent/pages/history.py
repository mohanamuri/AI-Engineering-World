"""History and download page for HR Multi-Agent panel."""

import json
from datetime import datetime, timezone
import streamlit as st
from applications.hr_multi_agent.constants import PANEL_RUN_HISTORY_SESSION_KEY


def render() -> None:
    st.header("📜 History")
    history = st.session_state.get(PANEL_RUN_HISTORY_SESSION_KEY, [])
    if not history:
        st.info("No panel runs yet.")
        return
    for i, result in enumerate(reversed(history), 1):
        label = f"#{len(history)-i+1} · {result.employee.get('JobRole','Employee')} · {result.risk_level}"
        with st.expander(label):
            st.markdown(result.final_answer)
