"""UC1 — Insights page: key learnings from zero-shot vs few-shot."""

import streamlit as st

from applications.prompt_projects.uc1.constants import (
    FEW_SHOT_RESULT_KEY,
    ZERO_SHOT_RESULT_KEY,
)


def render() -> None:
    st.subheader("💡 Insights — Zero-shot vs Few-shot")

    zs = st.session_state.get(ZERO_SHOT_RESULT_KEY)
    fs = st.session_state.get(FEW_SHOT_RESULT_KEY)

    if zs or fs:
        st.markdown("#### Your run metrics")
        col1, col2, col3, col4 = st.columns(4)
        if zs:
            col1.metric("Zero-shot latency", f"{zs.latency_ms:.0f} ms")
            col2.metric("Zero-shot tokens in", zs.tokens_in)
        if fs:
            col3.metric("Few-shot latency", f"{fs.latency_ms:.0f} ms")
            col4.metric("Few-shot tokens in", fs.tokens_in)
        if zs and fs:
            overhead = fs.tokens_in - zs.tokens_in
            st.info(f"Few-shot used **{overhead} extra prompt tokens** to provide examples — "
                    f"that's the trade-off: more context in, better-calibrated output out.")
        st.divider()

    st.markdown("#### When each technique wins")
    st.table({
        "Scenario": [
            "Simple factual question",
            "Custom output format",
            "Specific tone/style",
            "Novel domain knowledge",
            "Low-latency production API",
            "Consistent label classification",
        ],
        "Zero-shot": ["✅ Best", "⚠️ May vary", "⚠️ May vary", "✅ Relies on pretrain", "✅ Fewer tokens", "⚠️ Inconsistent"],
        "Few-shot": ["⚠️ Overkill", "✅ Best", "✅ Best", "⚠️ Examples needed", "⚠️ More tokens", "✅ Best"],
    })

    st.divider()
    st.markdown("#### Rules for writing good few-shot examples")
    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown("**✅ Do**")
            st.markdown(
                "- Use diverse examples (don't repeat the same input pattern)\n"
                "- Keep examples short — only as long as necessary\n"
                "- Order examples from simple to complex\n"
                "- Match the exact output format you want\n"
                "- Use 2–5 examples (more rarely helps)"
            )

    with col_b:
        with st.container(border=True):
            st.markdown("**❌ Don't**")
            st.markdown(
                "- Use biased or unrepresentative examples\n"
                "- Exceed 5 examples (diminishing returns, higher cost)\n"
                "- Include examples that contradict each other\n"
                "- Use overly long examples (dilutes the signal)\n"
                "- Skip zero-shot first — always try it before few-shot"
            )

    st.divider()
    st.markdown("#### What to try next")
    st.success(
        "**UC2 — Chain-of-Thought:** Instead of examples, guide the model to reason step by step. "
        "CoT is especially powerful for math, logic, and multi-step problems — "
        "without needing any examples at all."
    )
