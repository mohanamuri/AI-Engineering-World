"""Download page for HR Agent assessment reports."""

import json
from datetime import datetime, timezone
import streamlit as st
from applications.hr_agent.constants import AGENT_RUN_HISTORY_SESSION_KEY


def render() -> None:
    st.header("⬇ Download")
    history = st.session_state.get(AGENT_RUN_HISTORY_SESSION_KEY, [])
    if not history:
        st.info("Run at least one agent assessment first.")
        return

    latest = history[-1]
    st.subheader("Latest report")
    st.download_button(
        "Download latest report (.txt)",
        data=latest.final_answer.encode(),
        file_name=f"hr_risk_report_{latest.risk_level.lower()}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    payload = [
        {"employee": r.employee, "risk_level": r.risk_level, "risk_score": r.risk_score,
         "report": r.final_answer, "timestamp": r.timestamp}
        for r in history
    ]
    st.download_button(
        "Download all reports (.json)",
        data=json.dumps({"exported_at": datetime.now(timezone.utc).isoformat(),
                         "assessments": payload}, indent=2).encode(),
        file_name="hr_agent_all_reports.json",
        mime="application/json",
        use_container_width=True,
    )
