"""UC4 — Run page: Research Team."""

import streamlit as st

from applications.mas_projects.services.research_team import (
    ResearchTeamConfig,
    ResearchTeamRun,
    ResearchTrace,
    run_research_team,
)
from applications.mas_projects.uc4.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
    RUN_HISTORY_SESSION_KEY,
)

_SAMPLE_QUERIES = [
    "How does climate change affect global food security?",
    "What are the key factors behind the rise of large language models?",
    "How does the human immune system fight viral infections?",
    "What caused the 2008 financial crisis and what were the long-term effects?",
]

_ROLE_ICONS = {
    "planner":    "📋",
    "researcher": "🔎",
    "analyst":    "📊",
    "writer":     "📝",
}


def render() -> None:
    st.subheader("▶️ Run")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: ResearchTeamConfig = st.session_state.get(
        AGENT_CONFIG_SESSION_KEY, ResearchTeamConfig()
    )
    history: list[ResearchTeamRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.markdown("**Try a sample research query:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_QUERIES):
            if cols[i % 2].button(q, key=f"mas_uc4_sample_{i}", use_container_width=True):
                _run_research(q, config)
                st.rerun()
        st.divider()

    for run in history:
        with st.chat_message("user"):
            st.write(run.query)
        with st.chat_message("assistant"):
            st.write(run.report)
            researcher_steps = sum(1 for t in run.traces if t.role == "researcher")
            st.caption(
                f"Research questions answered: {researcher_steps}  ·  "
                f"Total agent steps: {len(run.traces)}"
            )
            with st.expander("Full research trace", expanded=False):
                _render_trace(run.traces)

    query = st.chat_input("Enter a research query…")
    if query:
        _run_research(query, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear research history"):
            st.session_state[RUN_HISTORY_SESSION_KEY] = []
            st.rerun()


def _render_trace(traces: list[ResearchTrace]) -> None:
    for trace in traces:
        icon = _ROLE_ICONS.get(trace.role, "•")
        st.markdown(f"**{icon} {trace.role.upper()}** — {trace.action}")
        st.caption(trace.output[:300] + ("…" if len(trace.output) > 300 else ""))


def _run_research(query: str, config: ResearchTeamConfig) -> None:
    with st.spinner("Research team working…"):
        try:
            result = run_research_team(query, config)
        except Exception as exc:
            st.error(f"Research team failed: {exc}")
            return
    history: list[ResearchTeamRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[RUN_HISTORY_SESSION_KEY] = history
