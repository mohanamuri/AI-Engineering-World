"""UC2 — Compare page: direct vs CoT side by side."""

import streamlit as st

from applications.prompt_projects.services.prompt_service import (
    PromptConfig,
    run_cot,
    run_direct,
)
from applications.prompt_projects.uc2.constants import (
    COT_RESULT_KEY,
    CONFIG_SESSION_KEY,
    DIRECT_RESULT_KEY,
    QUESTION_SESSION_KEY,
)


def render() -> None:
    st.subheader("⚖️ Direct vs Chain-of-Thought")
    st.write("Run both techniques on the same question and compare reasoning quality.")

    config: PromptConfig = st.session_state.get(CONFIG_SESSION_KEY, PromptConfig(temperature=0.3))
    saved_q = st.session_state.get(QUESTION_SESSION_KEY, "")

    question = st.text_area(
        "Question",
        value=saved_q,
        height=80,
        placeholder="e.g. A bat and ball cost $1.10. The bat costs $1 more. How much is the ball?",
    )

    if st.button("⚖️ Run Both", type="primary", disabled=not question, use_container_width=True):
        st.session_state[QUESTION_SESSION_KEY] = question
        col1, col2 = st.columns(2)
        with col1:
            with st.spinner("Running Direct…"):
                try:
                    dr = run_direct(question, config)
                    st.session_state[DIRECT_RESULT_KEY] = dr
                except Exception as exc:
                    st.error(f"Direct failed: {exc}")
                    return
        with col2:
            with st.spinner("Running Chain-of-Thought…"):
                try:
                    cr = run_cot(question, config)
                    st.session_state[COT_RESULT_KEY] = cr
                except Exception as exc:
                    st.error(f"CoT failed: {exc}")
                    return

    dr = st.session_state.get(DIRECT_RESULT_KEY)
    cr = st.session_state.get(COT_RESULT_KEY)

    if not dr and not cr:
        st.info("Enter a question and click **Run Both** to compare.")
        return

    st.divider()
    col_d, col_c = st.columns(2)

    with col_d:
        st.markdown("### 🚀 Direct")
        if dr:
            c1, c2 = st.columns(2)
            c1.metric("Latency", f"{dr.latency_ms:.0f} ms")
            c2.metric("Tokens out", dr.tokens_out)
            with st.container(border=True):
                st.markdown(dr.output)
            with st.expander("Prompt sent", expanded=False):
                st.code(dr.prompt_used, language="text")

    with col_c:
        st.markdown("### 🔗 Chain-of-Thought")
        if cr:
            c1, c2 = st.columns(2)
            c1.metric("Latency", f"{cr.latency_ms:.0f} ms")
            c2.metric("Tokens out", cr.tokens_out)
            with st.container(border=True):
                st.markdown(cr.output)
            with st.expander("Prompt sent", expanded=False):
                st.code(cr.prompt_used, language="text")

    if dr and cr:
        st.divider()
        extra = cr.tokens_out - dr.tokens_out
        st.metric(
            "Extra output tokens (CoT vs Direct)",
            extra,
            help="CoT generates more tokens — the reasoning steps — before the final answer.",
        )
