"""UC2 — History page."""

import streamlit as st

from applications.agent_projects.services.plan_execute_agent import PlanExecuteRun
from applications.agent_projects.uc2.constants import RUN_HISTORY_SESSION_KEY


def render() -> None:
    st.subheader("📜 History")

    history: list[PlanExecuteRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No runs yet. Go to **Run** to execute the agent.")
        return

    st.caption(f"{len(history)} run(s) this session")

    for i, run in enumerate(reversed(history)):
        n = len(history) - i
        label = f"Run {n}: {run.task[:70]}{'…' if len(run.task) > 70 else ''}"
        with st.expander(label, expanded=(i == 0)):
            col1, col2, col3 = st.columns(3)
            col1.metric("Plan steps", len(run.plan))
            col2.metric("Steps executed", len(run.step_results))
            tool_uses = sum(1 for s in run.step_results if s.tool_used)
            col3.metric("Tool calls", tool_uses)

            st.markdown("**Plan**")
            for j, step in enumerate(run.plan, 1):
                st.caption(f"{j}. {step}")

            st.markdown("**Step-by-step execution**")
            for sr in run.step_results:
                tool_badge = f" `{sr.tool_used}`" if sr.tool_used else " `LLM`"
                st.markdown(f"**Step {sr.step_number}**{tool_badge}")
                st.caption(f"Instruction: {sr.instruction}")
                st.caption(f"Result: {sr.result[:300]}{'…' if len(sr.result) > 300 else ''}")

            st.markdown("**Final answer**")
            st.write(run.answer)
            st.caption(f"Timestamp: {run.timestamp}")
