"""UC4 — Run page. Multi-Agent Supervisor execution."""

import streamlit as st

from applications.agent_projects.services.multi_agent import (
    AgentTrace,
    MultiAgentConfig,
    MultiAgentRun,
    run_multi_agent,
)
from applications.agent_projects.uc4.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
    RUN_HISTORY_SESSION_KEY,
)

_SAMPLE_TASKS = [
    "What is the population of Tokyo and how does it compare to New York?",
    "Research machine learning and estimate how many parameters GPT-3 has in billions.",
    "What is the speed of light and how long does it take to reach Mars (225M km away)?",
    "Explain blockchain technology and calculate how many hashes are in 2**32.",
]

_AGENT_ICONS = {
    "supervisor": "🧭",
    "researcher": "🔍",
    "analyst":    "🧮",
    "writer":     "✍️",
}


def render() -> None:
    st.subheader("▶️ Run")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: MultiAgentConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, MultiAgentConfig())
    history: list[MultiAgentRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.markdown("**Try a sample task:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_TASKS):
            if cols[i % 2].button(q, key=f"uc4_sample_{i}", use_container_width=True):
                _run_task(q, config)
                st.rerun()
        st.divider()

    for run in history:
        with st.chat_message("user"):
            st.write(run.task)
        with st.chat_message("assistant"):
            st.write(run.answer)
            agents_used = list(dict.fromkeys(
                t.agent_name for t in run.agent_traces if t.agent_name != "supervisor"
            ))
            st.caption(
                f"Agents involved: {', '.join(agents_used) or 'none'}  ·  "
                f"Total actions: {len(run.agent_traces)}"
            )
            with st.expander("Agent coordination trace", expanded=False):
                _render_trace(run.agent_traces)

    task = st.chat_input("Enter a task for the agent team…")
    if task:
        _run_task(task, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear run history"):
            st.session_state[RUN_HISTORY_SESSION_KEY] = []
            st.rerun()


def _render_trace(traces: list[AgentTrace]) -> None:
    for trace in traces:
        icon = _AGENT_ICONS.get(trace.agent_name, "•")
        st.markdown(f"**{icon} {trace.agent_name.upper()}** — {trace.action}")
        if trace.agent_name != "supervisor":
            st.caption(trace.output[:300] + ("…" if len(trace.output) > 300 else ""))


def _run_task(task: str, config: MultiAgentConfig) -> None:
    with st.spinner("Agent team is coordinating…"):
        try:
            result = run_multi_agent(task, config)
        except Exception as exc:
            st.error(f"Agent run failed: {exc}")
            return
    history: list[MultiAgentRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[RUN_HISTORY_SESSION_KEY] = history
