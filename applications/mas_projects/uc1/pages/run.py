"""UC1 — Run page: Supervisor Pipeline."""

import streamlit as st

from applications.mas_projects.services.supervisor_pipeline import (
    PipelineTrace,
    SupervisorPipelineConfig,
    SupervisorPipelineRun,
    run_supervisor_pipeline,
)
from applications.mas_projects.uc1.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
    RUN_HISTORY_SESSION_KEY,
)

_SAMPLE_TASKS = [
    "What is machine learning and what industries does it impact most?",
    "Explain how solar panels work and their current efficiency rates.",
    "What is the history of the internet and how has it changed communication?",
    "Describe how vaccines work and their impact on public health.",
]

_STAGE_ICONS = {
    "collector":  "🗂️",
    "processor":  "🔬",
    "writer":     "✍️",
    "supervisor": "🧭",
}


def render() -> None:
    st.subheader("▶️ Run")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: SupervisorPipelineConfig = st.session_state.get(
        AGENT_CONFIG_SESSION_KEY, SupervisorPipelineConfig()
    )
    history: list[SupervisorPipelineRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.markdown("**Try a sample task:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_TASKS):
            if cols[i % 2].button(q, key=f"mas_uc1_sample_{i}", use_container_width=True):
                _run_task(q, config)
                st.rerun()
        st.divider()

    for run in history:
        with st.chat_message("user"):
            st.write(run.task)
        with st.chat_message("assistant"):
            st.write(run.summary)
            st.caption(f"Pipeline stages completed: {len(run.traces)}")
            with st.expander("Pipeline execution trace", expanded=False):
                _render_trace(run.traces)

    task = st.chat_input("Enter a task for the pipeline…")
    if task:
        _run_task(task, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear run history"):
            st.session_state[RUN_HISTORY_SESSION_KEY] = []
            st.rerun()


def _render_trace(traces: list[PipelineTrace]) -> None:
    for trace in traces:
        icon = _STAGE_ICONS.get(trace.stage, "•")
        st.markdown(f"**{icon} {trace.stage.upper()}** — {trace.action}")
        st.caption(trace.output[:300] + ("…" if len(trace.output) > 300 else ""))


def _run_task(task: str, config: SupervisorPipelineConfig) -> None:
    with st.spinner("Pipeline running…"):
        try:
            result = run_supervisor_pipeline(task, config)
        except Exception as exc:
            st.error(f"Pipeline failed: {exc}")
            return
    history: list[SupervisorPipelineRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[RUN_HISTORY_SESSION_KEY] = history
