"""Download exports — page 5 of the loan agent workflow."""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import streamlit as st

from applications.loan_agent.constants import (
    HISTORY_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    RUN_RESULT_SESSION_KEY,
)
from applications.loan_agent.services.agent_graph import AgentRunResult
from applications.shared.api_reference import render_api_reference


def render() -> None:
    st.header("⬇ Download")
    st.caption("Export decision reports and run history as JSON or CSV.")

    result: AgentRunResult | None = st.session_state.get(RUN_RESULT_SESSION_KEY)
    history: list[AgentRunResult] = st.session_state.get(HISTORY_SESSION_KEY, [])

    m1, m2 = st.columns(2)
    m1.metric("Latest decision", result.decision if result else "—")
    m2.metric("Total in history", len(history))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### Latest decision (JSON)")
            st.caption("Full report: application, tool steps, decision, reasoning.")
            if result:
                st.download_button(
                    label="Download decision_report.json",
                    data=_result_to_json(result),
                    file_name="loan_agent_decision.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_latest",
                )
            else:
                st.info("Run the agent first.")

    with col2:
        with st.container(border=True):
            st.markdown("#### Full history (JSON)")
            st.caption("All decisions from this session.")
            if history:
                st.download_button(
                    label="Download history.json",
                    data=_history_to_json(history),
                    file_name="loan_agent_history.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_history_json",
                )
            else:
                st.info("No history yet.")

    with st.container(border=True):
        st.markdown("#### History (CSV)")
        st.caption("Flat table: applicant, loan details, decision, timestamp.")
        if history:
            st.download_button(
                label="Download history.csv",
                data=_history_to_csv(history),
                file_name="loan_agent_history.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_history_csv",
            )
        else:
            st.info("No history yet.")

    if result:
        st.divider()
        st.subheader("How to reproduce with LangGraph")
        st.code(
            """from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.tools import tool
import json

# 1. Define your tools (validate, score_risk, lookup_policy)
@tool
def validate_application(application_json: str) -> str:
    \"\"\"Validate loan application fields.\"\"\"
    ...  # see agent_tools.py

# 2. Build the agent
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.0)
agent = create_react_agent(llm, [validate_application, ...], prompt=SYSTEM_PROMPT)

# 3. Run
application = {"applicant_name": "...", "credit_score": 720, ...}
result = agent.invoke({"messages": [("user", json.dumps(application))]})

# 4. Parse steps
for msg in result["messages"]:
    if hasattr(msg, "tool_calls"):
        print("Tool call:", msg.tool_calls)
""",
            language="python",
        )
    render_api_reference("loan_agent", "download")


# ---------------------------------------------------------------------------
# Serialisers
# ---------------------------------------------------------------------------

def _result_to_json(result: AgentRunResult) -> bytes:
    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "decision": result.decision,
        "timestamp": result.timestamp,
        "application": result.application,
        "final_answer": result.final_answer,
        "tool_steps": [
            {
                "tool": s.tool_name,
                "input": s.tool_input,
                "output": s.tool_output,
            }
            for s in result.steps
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")


def _history_to_json(history: list[AgentRunResult]) -> bytes:
    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "count": len(history),
        "decisions": [json.loads(_result_to_json(r)) for r in history],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")


def _history_to_csv(history: list[AgentRunResult]) -> bytes:
    import csv
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "#", "applicant_name", "loan_type", "loan_amount_usd",
        "credit_score", "monthly_income_usd", "decision", "timestamp",
    ])
    for i, r in enumerate(history, 1):
        app = r.application
        writer.writerow([
            i,
            app.get("applicant_name", ""),
            app.get("loan_type", ""),
            app.get("loan_amount_usd", ""),
            app.get("credit_score", ""),
            app.get("monthly_income_usd", ""),
            r.decision,
            r.timestamp[:10],
        ])
    return buf.getvalue().encode("utf-8")
