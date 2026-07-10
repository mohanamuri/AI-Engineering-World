"""UC4 — History page."""

import streamlit as st

from applications.agent_projects.services.multi_agent import MultiAgentRun
from applications.agent_projects.uc4.constants import RUN_HISTORY_SESSION_KEY

_AGENT_ICONS = {
    "supervisor": "🧭",
    "researcher": "🔍",
    "analyst":    "🧮",
    "writer":     "✍️",
}


def render() -> None:
    st.subheader("📜 History")

    history: list[MultiAgentRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No runs yet. Go to **Run** to execute the agent team.")
        return

    st.caption(f"{len(history)} run(s) this session")

    for i, run in enumerate(reversed(history)):
        n = len(history) - i
        label = f"Run {n}: {run.task[:70]}{'…' if len(run.task) > 70 else ''}"
        with st.expander(label, expanded=(i == 0)):
            agents_used = list(dict.fromkeys(
                t.agent_name for t in run.agent_traces if t.agent_name != "supervisor"
            ))
            col1, col2, col3 = st.columns(3)
            col1.metric("Specialists used", len(agents_used))
            col2.metric("Total actions", len(run.agent_traces))
            col3.metric("Specialists", ", ".join(agents_used) or "none")

            st.markdown("**Final answer**")
            st.write(run.answer)

            st.markdown("**Agent coordination trace**")
            for trace in run.agent_traces:
                icon = _AGENT_ICONS.get(trace.agent_name, "•")
                st.markdown(f"{icon} **{trace.agent_name.upper()}** — {trace.action}")
                if trace.agent_name != "supervisor":
                    st.caption(trace.output[:300] + ("…" if len(trace.output) > 300 else ""))

            st.caption(f"Timestamp: {run.timestamp}")
