"""UC4 — Compare page: single prompt vs chain side by side."""

import streamlit as st

from applications.prompt_projects.services.prompt_service import (
    PromptConfig,
    run_chain,
    run_single_prompt,
)
from applications.prompt_projects.uc4.constants import (
    CHAIN_RESULT_KEY,
    CONFIG_SESSION_KEY,
    SINGLE_RESULT_KEY,
    TASK_SESSION_KEY,
)


def render() -> None:
    st.subheader("⚖️ Single Prompt vs Chain")
    st.write("Run both on the same task and compare depth, quality, and token cost.")

    config: PromptConfig = st.session_state.get(CONFIG_SESSION_KEY, PromptConfig())
    saved_task = st.session_state.get(TASK_SESSION_KEY, "")

    task = st.text_area(
        "Task",
        value=saved_task,
        height=80,
        placeholder="e.g. Write a blog post about AI in healthcare.",
    )

    if st.button("⚖️ Run Both", type="primary", disabled=not task, use_container_width=True):
        st.session_state[TASK_SESSION_KEY] = task
        col1, col2 = st.columns(2)
        with col1:
            with st.spinner("Running Single Prompt…"):
                try:
                    sr = run_single_prompt(task, config)
                    st.session_state[SINGLE_RESULT_KEY] = sr
                except Exception as exc:
                    st.error(f"Single prompt failed: {exc}")
                    return
        with col2:
            with st.spinner("Running Chain (3 steps)…"):
                try:
                    cr = run_chain(task, config)
                    st.session_state[CHAIN_RESULT_KEY] = cr
                except Exception as exc:
                    st.error(f"Chain failed: {exc}")
                    return

    sr = st.session_state.get(SINGLE_RESULT_KEY)
    cr = st.session_state.get(CHAIN_RESULT_KEY)

    if not sr and not cr:
        st.info("Enter a task and click **Run Both** to compare.")
        return

    st.divider()
    col_s, col_c = st.columns(2)

    with col_s:
        st.markdown("### 📄 Single Prompt")
        if sr:
            c1, c2 = st.columns(2)
            c1.metric("Latency", f"{sr.latency_ms:.0f} ms")
            c2.metric("Tokens out", sr.tokens_out)
            with st.container(border=True):
                st.markdown(sr.output)

    with col_c:
        st.markdown("### 🔗 Chain (3 steps)")
        if cr:
            c1, c2 = st.columns(2)
            c1.metric("Total latency", f"{cr.total_latency_ms:.0f} ms")
            c2.metric("Total tokens out", cr.total_tokens_out)
            for step in cr.steps:
                with st.expander(f"**{step.label}**", expanded=False):
                    st.markdown(step.output)
                    st.caption(f"{step.latency_ms:.0f} ms · {step.tokens_out} tok")
            st.divider()
            st.markdown("**Final refined output:**")
            with st.container(border=True):
                st.markdown(cr.final_output)

    if sr and cr:
        st.divider()
        extra_lat = cr.total_latency_ms - sr.latency_ms
        extra_tok = cr.total_tokens_out - sr.tokens_out
        c1, c2 = st.columns(2)
        c1.metric("Extra latency (chain overhead)", f"{extra_lat:.0f} ms")
        c2.metric("Extra output tokens (chain)", extra_tok)
        st.info("The chain costs more tokens and time — judge whether the quality gain is worth it for your use case.")
