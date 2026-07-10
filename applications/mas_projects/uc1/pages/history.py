"""UC1 — History page: Supervisor Pipeline."""

import streamlit as st

from applications.mas_projects.services.supervisor_pipeline import SupervisorPipelineRun
from applications.mas_projects.uc1.constants import RUN_HISTORY_SESSION_KEY

_STAGE_ICONS = {
    "collector":  "🗂️",
    "processor":  "🔬",
    "writer":     "✍️",
    "supervisor": "🧭",
}


def render() -> None:
    st.subheader("📜 History")

    history: list[SupervisorPipelineRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No runs yet. Go to **Run** to execute the pipeline.")
        return

    st.caption(f"{len(history)} run(s) this session")

    for i, run in enumerate(reversed(history)):
        n = len(history) - i
        label = f"Run {n}: {run.task[:70]}{'…' if len(run.task) > 70 else ''}"
        with st.expander(label, expanded=(i == 0)):
            col1, col2 = st.columns(2)
            col1.metric("Pipeline stages", len(run.traces))
            col2.metric("Timestamp", run.timestamp[:19].replace("T", " "))

            st.markdown("**Executive summary**")
            st.write(run.summary)

            st.markdown("**Pipeline execution trace**")
            for trace in run.traces:
                icon = _STAGE_ICONS.get(trace.stage, "•")
                st.markdown(f"{icon} **{trace.stage.upper()}** — {trace.action}")
                st.caption(trace.output[:300] + ("…" if len(trace.output) > 300 else ""))
