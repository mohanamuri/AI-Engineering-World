"""UC2 — History page: Parallel Agents."""

import streamlit as st

from applications.mas_projects.services.parallel_agents import ParallelAgentsRun
from applications.mas_projects.uc2.constants import RUN_HISTORY_SESSION_KEY

_AGENT_ICONS = {
    "facts":      "📊",
    "critic":     "🔍",
    "creative":   "💡",
    "aggregator": "🔀",
}


def render() -> None:
    st.subheader("📜 History")

    history: list[ParallelAgentsRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No runs yet. Go to **Run** to execute the parallel agents.")
        return

    st.caption(f"{len(history)} run(s) this session")

    for i, run in enumerate(reversed(history)):
        n = len(history) - i
        label = f"Run {n}: {run.task[:70]}{'…' if len(run.task) > 70 else ''}"
        with st.expander(label, expanded=(i == 0)):
            col1, col2 = st.columns(2)
            col1.metric("Agent perspectives", len([t for t in run.traces if t.agent != "aggregator"]))
            col2.metric("Timestamp", run.timestamp[:19].replace("T", " "))

            st.markdown("**Aggregated answer**")
            st.write(run.answer)

            st.markdown("**Individual perspectives**")
            for trace in run.traces:
                if trace.agent == "aggregator":
                    continue
                icon = _AGENT_ICONS.get(trace.agent, "•")
                st.markdown(f"{icon} **{trace.perspective}**")
                st.caption(trace.output[:300] + ("…" if len(trace.output) > 300 else ""))
