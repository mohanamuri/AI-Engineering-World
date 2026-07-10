"""
UC1 — History page.

Review past ReAct agent runs with full trace details.
"""

import streamlit as st

from applications.agent_projects.services.react_agent import ReactRun
from applications.agent_projects.uc1.constants import RUN_HISTORY_SESSION_KEY

_STEP_ICONS = {
    "thought":     "🤔",
    "tool_call":   "🔧",
    "tool_result": "📋",
    "answer":      "✅",
}


def render() -> None:
    st.subheader("📜 History")

    history: list[ReactRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No runs yet. Go to **Run** to execute the agent.")
        return

    st.caption(f"{len(history)} run(s) this session")

    for i, run in enumerate(reversed(history)):
        n = len(history) - i
        label = f"Run {n}: {run.task[:70]}{'…' if len(run.task) > 70 else ''}"
        with st.expander(label, expanded=(i == 0)):
            col1, col2, col3 = st.columns(3)
            col1.metric("Iterations", run.iterations)
            col2.metric("Trace steps", len(run.steps))
            tool_calls = sum(1 for s in run.steps if s.step_type == "tool_call")
            col3.metric("Tool calls", tool_calls)

            st.markdown("**Final answer**")
            st.write(run.answer)

            st.markdown("**Agent trace**")
            for step in run.steps:
                icon = _STEP_ICONS.get(step.step_type, "•")
                st.markdown(f"{icon} **{step.content}**")
                if step.detail:
                    st.caption(step.detail)

            st.caption(f"Timestamp: {run.timestamp}")
