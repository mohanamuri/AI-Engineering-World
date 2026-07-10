"""UC1 — Compare page: run zero-shot and few-shot side by side."""

import streamlit as st

from applications.prompt_projects.services.prompt_service import (
    PromptConfig,
    run_few_shot,
    run_zero_shot,
)
from applications.prompt_projects.uc1.constants import (
    CONFIG_SESSION_KEY,
    FEW_SHOT_RESULT_KEY,
    TASK_SESSION_KEY,
    ZERO_SHOT_RESULT_KEY,
)

_DEFAULT_EXAMPLES = [
    {"input": "Write a tagline for a fitness app called StrongMe.", "output": "StrongMe — built for the version of you that never quits."},
    {"input": "Write a tagline for a finance app called ClearCash.", "output": "ClearCash — every dollar, perfectly in focus."},
]


def render() -> None:
    st.subheader("⚖️ Side-by-side Comparison")
    st.write("Run both techniques on the same task and compare outputs, token usage, and latency.")

    config: PromptConfig = st.session_state.get(CONFIG_SESSION_KEY, PromptConfig())
    saved_task = st.session_state.get(TASK_SESSION_KEY, "")

    task = st.text_area(
        "Task for comparison",
        value=saved_task,
        height=80,
        placeholder="e.g. Write a tagline for a coffee brand called MorningBrew.",
    )

    if st.button("⚖️ Run Both", type="primary", disabled=not task, use_container_width=True):
        st.session_state[TASK_SESSION_KEY] = task
        col_spin1, col_spin2 = st.columns(2)
        with col_spin1:
            with st.spinner("Running Zero-shot…"):
                try:
                    zs = run_zero_shot(task, config)
                    st.session_state[ZERO_SHOT_RESULT_KEY] = zs
                except Exception as exc:
                    st.error(f"Zero-shot failed: {exc}")
                    return
        with col_spin2:
            with st.spinner("Running Few-shot…"):
                try:
                    fs = run_few_shot(task, _DEFAULT_EXAMPLES, config)
                    st.session_state[FEW_SHOT_RESULT_KEY] = fs
                except Exception as exc:
                    st.error(f"Few-shot failed: {exc}")
                    return

    zs_result = st.session_state.get(ZERO_SHOT_RESULT_KEY)
    fs_result = st.session_state.get(FEW_SHOT_RESULT_KEY)

    if not zs_result and not fs_result:
        st.info("Enter a task above and click **Run Both** to see the comparison.")
        return

    st.divider()
    col_zs, col_fs = st.columns(2)

    with col_zs:
        st.markdown("### ⚡ Zero-shot")
        if zs_result:
            c1, c2 = st.columns(2)
            c1.metric("Latency", f"{zs_result.latency_ms:.0f} ms")
            c2.metric("Tokens out", zs_result.tokens_out)
            with st.container(border=True):
                st.markdown(zs_result.output)
            with st.expander("Prompt sent", expanded=False):
                st.code(zs_result.prompt_used, language="text")
        else:
            st.info("No zero-shot result yet.")

    with col_fs:
        st.markdown("### 🎯 Few-shot")
        if fs_result:
            c1, c2 = st.columns(2)
            c1.metric("Latency", f"{fs_result.latency_ms:.0f} ms")
            c2.metric("Tokens out", fs_result.tokens_out)
            with st.container(border=True):
                st.markdown(fs_result.output)
            with st.expander("Prompt sent", expanded=False):
                st.code(fs_result.prompt_used, language="text")
        else:
            st.info("No few-shot result yet.")

    if zs_result and fs_result:
        st.divider()
        st.markdown("#### Token overhead of few-shot")
        extra_tokens = fs_result.tokens_in - zs_result.tokens_in
        st.metric(
            "Extra prompt tokens (few-shot vs zero-shot)",
            extra_tokens,
            help="This is the cost of adding examples — worth it if quality improves.",
        )
