"""UC3 — Run page. Reflection agent execution."""

import streamlit as st

from applications.agent_projects.services.reflection_agent import (
    DraftRecord,
    ReflectionConfig,
    ReflectionRun,
    run_reflection_agent,
)
from applications.agent_projects.uc3.constants import (
    AGENT_CONFIG_SESSION_KEY,
    AGENT_SETUP_SESSION_KEY,
    RUN_HISTORY_SESSION_KEY,
)

_SAMPLE_TASKS = [
    "Explain the difference between supervised and unsupervised learning.",
    "Write a brief explanation of how transformer models work.",
    "Describe the key principles of clean code in software engineering.",
    "Explain what gradient descent is and how it's used in machine learning.",
]


def _score_color(score: int, threshold: int) -> str:
    if score >= threshold:
        return "🟢"
    if score >= threshold - 1:
        return "🟡"
    return "🔴"


def render() -> None:
    st.subheader("▶️ Run")

    setup = st.session_state.get(AGENT_SETUP_SESSION_KEY)
    if setup is None:
        st.warning("Complete **Setup** first.")
        return

    config: ReflectionConfig = st.session_state.get(AGENT_CONFIG_SESSION_KEY, ReflectionConfig())
    history: list[ReflectionRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])

    if not history:
        st.markdown("**Try a sample task:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_TASKS):
            if cols[i % 2].button(q, key=f"uc3_sample_{i}", use_container_width=True):
                _run_task(q, config)
                st.rerun()
        st.divider()

    for run in history:
        with st.chat_message("user"):
            st.write(run.task)
        with st.chat_message("assistant"):
            st.write(run.final_answer)
            last = run.drafts[-1] if run.drafts else None
            if last:
                passed = last.scores_ok(config.quality_threshold)
                verdict = "✅ Passed critique" if passed else f"⚠️ Best after {len(run.drafts)} draft(s)"
                st.caption(
                    f"{verdict}  ·  "
                    f"Clarity:{last.clarity} Accuracy:{last.accuracy} Completeness:{last.completeness}  ·  "
                    f"Avg:{last.avg}/5"
                )
            with st.expander("Draft history", expanded=False):
                _render_drafts(run.drafts, config.quality_threshold)

    task = st.chat_input("Enter a task for the Reflection agent…")
    if task:
        _run_task(task, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear run history"):
            st.session_state[RUN_HISTORY_SESSION_KEY] = []
            st.rerun()


def _render_drafts(drafts: list[DraftRecord], threshold: int) -> None:
    for dr in drafts:
        passed = dr.scores_ok(threshold)
        status = "✅ Passed" if passed else "❌ Failed"
        st.markdown(f"**Draft {dr.draft_number}** — {status}  (avg {dr.avg}/5)")
        c1, c2, c3 = st.columns(3)
        c1.metric(f"{_score_color(dr.clarity, threshold)} Clarity", f"{dr.clarity}/5")
        c2.metric(f"{_score_color(dr.accuracy, threshold)} Accuracy", f"{dr.accuracy}/5")
        c3.metric(f"{_score_color(dr.completeness, threshold)} Completeness", f"{dr.completeness}/5")
        if not passed and dr != drafts[-1]:
            st.caption("Draft revised for next attempt.")
        st.divider()


def _run_task(task: str, config: ReflectionConfig) -> None:
    with st.spinner("Generating and self-critiquing…"):
        try:
            result = run_reflection_agent(task, config)
        except Exception as exc:
            st.error(f"Agent run failed: {exc}")
            return
    history: list[ReflectionRun] = st.session_state.get(RUN_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[RUN_HISTORY_SESSION_KEY] = history
