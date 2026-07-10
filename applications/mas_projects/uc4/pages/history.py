"""UC4 — History page: Research Team."""

import streamlit as st

from applications.mas_projects.services.research_team import ResearchTeamRun
from applications.mas_projects.uc4.constants import RUN_HISTORY_SESSION_KEY

_ROLE_ICONS = {
    "planner":    "📋",
    "researcher": "🔎",
    "analyst":    "📊",
    "writer":     "📝",
}


def render() -> None:
    st.subheader("📜 History")

    history: list[ResearchTeamRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No research runs yet. Go to **Run** to deploy the research team.")
        return

    st.caption(f"{len(history)} run(s) this session")

    for i, run in enumerate(reversed(history)):
        n = len(history) - i
        label = f"Run {n}: {run.query[:70]}{'…' if len(run.query) > 70 else ''}"
        with st.expander(label, expanded=(i == 0)):
            researcher_steps = sum(1 for t in run.traces if t.role == "researcher")
            col1, col2, col3 = st.columns(3)
            col1.metric("Research questions", researcher_steps)
            col2.metric("Total agent steps", len(run.traces))
            col3.metric("Timestamp", run.timestamp[:19].replace("T", " "))

            st.markdown("**Final report**")
            st.write(run.report)

            st.markdown("**Full research trace**")
            for trace in run.traces:
                icon = _ROLE_ICONS.get(trace.role, "•")
                st.markdown(f"{icon} **{trace.role.upper()}** — {trace.action}")
                st.caption(trace.output[:300] + ("…" if len(trace.output) > 300 else ""))
