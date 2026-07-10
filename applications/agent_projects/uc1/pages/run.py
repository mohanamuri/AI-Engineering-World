"""
UC1 — Run page.

Interactive ReAct agent execution.  The user enters a task, the agent runs,
and the trace steps are shown alongside the final answer.
"""

import streamlit as st

from applications.agent_projects.services.react_agent import ReactConfig, ReactRun, run_react_agent
from applications.agent_projects.uc1.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
    RUN_HISTORY_SESSION_KEY,
)

_SAMPLE_TASKS = [
    "What is the population of Japan and how does it compare to Germany?",
    "Calculate the compound interest on $5000 at 7% for 10 years.",
    "What is Python and what is it primarily used for?",
    "How many seconds are in a year? Show your calculation.",
]

_STEP_ICONS = {
    "thought":     "🤔",
    "tool_call":   "🔧",
    "tool_result": "📋",
    "answer":      "✅",
}


def render() -> None:
    st.subheader("▶️ Run")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: ReactConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, ReactConfig())
    history: list[ReactRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    # --- Sample tasks ---
    if not history:
        st.markdown("**Try a sample task:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_TASKS):
            if cols[i % 2].button(q, key=f"uc1_sample_{i}", use_container_width=True):
                _run_task(q, config)
                st.rerun()
        st.divider()

    # --- Past runs in this session ---
    for run in history:
        with st.chat_message("user"):
            st.write(run.task)
        with st.chat_message("assistant"):
            st.write(run.answer)
            st.caption(f"Iterations: {run.iterations}  ·  Steps: {len(run.steps)}")
            with st.expander("Agent trace", expanded=False):
                _render_trace(run)

    # --- Task input ---
    task = st.chat_input("Enter a task for the ReAct agent…")
    if task:
        _run_task(task, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear run history"):
            st.session_state[RUN_HISTORY_SESSION_KEY] = []
            st.rerun()


def _render_trace(run: ReactRun) -> None:
    for step in run.steps:
        icon = _STEP_ICONS.get(step.step_type, "•")
        st.markdown(f"**{icon} {step.content}**")
        if step.detail:
            st.caption(step.detail)


def _run_task(task: str, config: ReactConfig) -> None:
    with st.spinner("Agent is reasoning and acting…"):
        try:
            result = run_react_agent(task, config)
        except Exception as exc:
            st.error(f"Agent run failed: {exc}")
            return
    history: list[ReactRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[RUN_HISTORY_SESSION_KEY] = history
