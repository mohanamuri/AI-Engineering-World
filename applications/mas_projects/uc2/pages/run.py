"""UC2 — Run page: Parallel Agents."""

import streamlit as st

from applications.mas_projects.services.parallel_agents import (
    ParallelAgentsConfig,
    ParallelAgentsRun,
    ParallelTrace,
    run_parallel_agents,
)
from applications.mas_projects.uc2.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
    RUN_HISTORY_SESSION_KEY,
)

_SAMPLE_TASKS = [
    "Should AI be used in hiring decisions?",
    "What is the impact of social media on mental health?",
    "Is nuclear energy a viable solution to climate change?",
    "How has remote work changed the future of cities?",
]

_AGENT_ICONS = {
    "facts":       "📊",
    "critic":      "🔍",
    "creative":    "💡",
    "aggregator":  "🔀",
}

_AGENT_COLORS = {
    "facts":      "#eef2ff",
    "critic":     "#fff1f2",
    "creative":   "#ecfdf5",
    "aggregator": "#fffbeb",
}


def render() -> None:
    st.subheader("▶️ Run")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: ParallelAgentsConfig = st.session_state.get(
        AGENT_CONFIG_SESSION_KEY, ParallelAgentsConfig()
    )
    history: list[ParallelAgentsRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.markdown("**Try a sample task:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_TASKS):
            if cols[i % 2].button(q, key=f"mas_uc2_sample_{i}", use_container_width=True):
                _run_task(q, config)
                st.rerun()
        st.divider()

    for run in history:
        with st.chat_message("user"):
            st.write(run.task)
        with st.chat_message("assistant"):
            st.write(run.answer)
            st.caption(f"Perspectives gathered: {len([t for t in run.traces if t.agent != 'aggregator'])}")
            with st.expander("Individual agent perspectives", expanded=False):
                _render_perspectives(run.traces)

    task = st.chat_input("Enter a task for the parallel team…")
    if task:
        _run_task(task, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear run history"):
            st.session_state[RUN_HISTORY_SESSION_KEY] = []
            st.rerun()


def _render_perspectives(traces: list[ParallelTrace]) -> None:
    specialist_traces = [t for t in traces if t.agent != "aggregator"]
    if specialist_traces:
        cols = st.columns(len(specialist_traces))
        for col, trace in zip(cols, specialist_traces):
            icon = _AGENT_ICONS.get(trace.agent, "•")
            with col:
                st.markdown(f"**{icon} {trace.perspective}**")
                st.caption(trace.output[:250] + ("…" if len(trace.output) > 250 else ""))

    agg = next((t for t in traces if t.agent == "aggregator"), None)
    if agg:
        st.divider()
        st.markdown(f"**🔀 {agg.perspective}**")
        st.write(agg.output)


def _run_task(task: str, config: ParallelAgentsConfig) -> None:
    with st.spinner("Three agents working in parallel…"):
        try:
            result = run_parallel_agents(task, config)
        except Exception as exc:
            st.error(f"Agent run failed: {exc}")
            return
    history: list[ParallelAgentsRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[RUN_HISTORY_SESSION_KEY] = history
