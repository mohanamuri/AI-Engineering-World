"""UC2 — Run page. Plan-and-Execute agent execution."""

import streamlit as st

from applications.agent_projects.services.plan_execute_agent import (
    PlanExecuteConfig,
    PlanExecuteRun,
    run_plan_execute_agent,
)
from applications.agent_projects.uc2.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
    RUN_HISTORY_SESSION_KEY,
)

_SAMPLE_TASKS = [
    "Compare the GDP of the USA, China, and Germany, then rank them.",
    "Explain quantum computing and calculate how many states 10 qubits can represent.",
    "What is climate change and what are three key statistics about it?",
    "Research the history of the internet and summarise its five key milestones.",
]


def render() -> None:
    st.subheader("▶️ Run")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: PlanExecuteConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, PlanExecuteConfig())
    history: list[PlanExecuteRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.markdown("**Try a sample task:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_TASKS):
            if cols[i % 2].button(q, key=f"uc2_sample_{i}", use_container_width=True):
                _run_task(q, config)
                st.rerun()
        st.divider()

    for run in history:
        with st.chat_message("user"):
            st.write(run.task)
        with st.chat_message("assistant"):
            st.write(run.answer)
            st.caption(f"Plan steps: {len(run.plan)}  ·  Steps executed: {len(run.step_results)}")
            with st.expander("Plan + execution trace", expanded=False):
                _render_run(run)

    task = st.chat_input("Enter a task for the Plan-and-Execute agent…")
    if task:
        _run_task(task, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear run history"):
            st.session_state[RUN_HISTORY_SESSION_KEY] = []
            st.rerun()


def _render_run(run: PlanExecuteRun) -> None:
    st.markdown("**Plan**")
    for i, step in enumerate(run.plan, 1):
        st.caption(f"{i}. {step}")

    st.markdown("**Execution**")
    for sr in run.step_results:
        tool_badge = f" `{sr.tool_used}`" if sr.tool_used else " `LLM`"
        st.markdown(f"**Step {sr.step_number}**{tool_badge} — {sr.instruction}")
        st.caption(sr.result[:300] + ("…" if len(sr.result) > 300 else ""))


def _run_task(task: str, config: PlanExecuteConfig) -> None:
    with st.spinner("Planning and executing…"):
        try:
            result = run_plan_execute_agent(task, config)
        except Exception as exc:
            st.error(f"Agent run failed: {exc}")
            return
    history: list[PlanExecuteRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[RUN_HISTORY_SESSION_KEY] = history
