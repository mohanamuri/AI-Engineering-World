"""Download page for HR Multi-Agent reports."""

import json
from datetime import datetime, timezone
import streamlit as st
from applications.hr_multi_agent.constants import PANEL_RUN_HISTORY_SESSION_KEY
from applications.shared.api_reference import render_api_reference


def render() -> None:
    st.header("⬇ Download")
    history = st.session_state.get(PANEL_RUN_HISTORY_SESSION_KEY, [])
    if not history:
        st.info("Run the panel first.")
        return
    latest = history[-1]
    st.download_button(
        "Download latest panel report (.txt)",
        data=latest.final_answer.encode(),
        file_name=f"hr_panel_report_{latest.risk_level.lower()}.txt",
        mime="text/plain",
        use_container_width=True,
    )
    payload = [
        {"employee": r.employee, "risk_level": r.risk_level,
         "director_decision": r.final_answer, "timestamp": r.timestamp,
         "specialists": {
             "hr_manager": {"rec": r.hr_manager_report.recommendation, "analysis": r.hr_manager_report.analysis},
             "performance_evaluator": {"rec": r.perf_evaluator_report.recommendation, "analysis": r.perf_evaluator_report.analysis},
             "risk_assessor": {"rec": r.risk_assessor_report.recommendation, "analysis": r.risk_assessor_report.analysis},
         }}
        for r in history
    ]
    st.download_button(
        "Download all panel reports (.json)",
        data=json.dumps({"exported_at": datetime.now(timezone.utc).isoformat(), "panels": payload}, indent=2).encode(),
        file_name="hr_multi_agent_reports.json",
        mime="application/json",
        use_container_width=True,
    )
    render_api_reference("hr_multi_agent", "download")
