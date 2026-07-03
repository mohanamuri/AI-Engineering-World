"""Download exports — page 5 of the multi-agent workflow."""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import streamlit as st

from applications.loan_multi_agent.constants import (
    HISTORY_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PANEL_RESULT_SESSION_KEY,
)
from applications.loan_multi_agent.services.panel_graph import PanelRunResult


def render() -> None:
    st.header("⬇ Download")
    st.caption("Export the full panel decision report and session history.")

    result: PanelRunResult | None = st.session_state.get(PANEL_RESULT_SESSION_KEY)
    history: list[PanelRunResult] = st.session_state.get(HISTORY_SESSION_KEY, [])

    m1, m2 = st.columns(2)
    m1.metric("Latest decision", result.decision if result else "—")
    m2.metric("Total in history", len(history))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### Full panel report (JSON)")
            st.caption("Application, all 3 specialist reports, tool steps, supervisor decision.")
            if result:
                st.download_button(
                    "Download panel_report.json",
                    data=_result_to_json(result),
                    file_name="loan_mas_panel_report.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_latest",
                )
            else:
                st.info("Run the panel first.")

    with col2:
        with st.container(border=True):
            st.markdown("#### Full history (CSV)")
            st.caption("All decisions: applicant, loan details, votes, final decision.")
            if history:
                st.download_button(
                    "Download history.csv",
                    data=_history_to_csv(history),
                    file_name="loan_mas_history.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_csv",
                )
            else:
                st.info("No history yet.")


def _result_to_json(result: PanelRunResult) -> bytes:
    def report_dict(r):
        return {
            "agent": r.agent_name,
            "role": r.agent_role,
            "recommendation": r.recommendation,
            "analysis": r.analysis,
            "tool_steps": [
                {"tool": s.tool_name, "input": s.tool_input, "output": s.tool_output}
                for s in r.tool_steps
            ],
        }

    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "decision": result.decision,
        "timestamp": result.timestamp,
        "application": result.application,
        "specialist_reports": [
            report_dict(result.underwriter_report),
            report_dict(result.fraud_report),
            report_dict(result.compliance_report),
        ],
        "supervisor_decision": result.final_answer,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")


def _history_to_csv(history: list[PanelRunResult]) -> bytes:
    import csv
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "#", "applicant", "loan_type", "amount_usd", "credit_score",
        "underwriter_vote", "fraud_vote", "compliance_vote", "decision", "date",
    ])
    for i, r in enumerate(history, 1):
        app = r.application
        writer.writerow([
            i,
            app.get("applicant_name", ""),
            app.get("loan_type", ""),
            app.get("loan_amount_usd", ""),
            app.get("credit_score", ""),
            r.underwriter_report.recommendation.replace("RECOMMEND_", ""),
            r.fraud_report.recommendation.replace("RECOMMEND_", ""),
            r.compliance_report.recommendation.replace("RECOMMEND_", ""),
            r.decision,
            r.timestamp[:10],
        ])
    return buf.getvalue().encode("utf-8")
