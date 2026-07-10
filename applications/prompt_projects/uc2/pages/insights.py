"""UC2 — Insights page: when CoT helps and when it doesn't."""

import streamlit as st

from applications.prompt_projects.uc2.constants import COT_RESULT_KEY, DIRECT_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Chain-of-Thought")

    dr = st.session_state.get(DIRECT_RESULT_KEY)
    cr = st.session_state.get(COT_RESULT_KEY)

    if dr or cr:
        st.markdown("#### Your run metrics")
        c1, c2, c3, c4 = st.columns(4)
        if dr:
            c1.metric("Direct latency", f"{dr.latency_ms:.0f} ms")
            c2.metric("Direct tokens out", dr.tokens_out)
        if cr:
            c3.metric("CoT latency", f"{cr.latency_ms:.0f} ms")
            c4.metric("CoT tokens out", cr.tokens_out)
        if dr and cr:
            overhead = cr.tokens_out - dr.tokens_out
            st.info(
                f"CoT generated **{overhead} more output tokens** — those are the reasoning steps. "
                "The model 'thinks' in tokens, so more thinking = more tokens = slightly higher latency."
            )
        st.divider()

    st.markdown("#### When CoT outperforms direct prompting")
    st.table({
        "Task type": [
            "Arithmetic / algebra",
            "Logical deduction",
            "Multi-step planning",
            "Code debugging",
            "Trade-off analysis",
            "Simple factual Q&A",
            "Short creative writing",
            "Classification",
        ],
        "Use CoT?": ["✅ Always", "✅ Always", "✅ Yes", "✅ Yes", "✅ Yes", "❌ Overkill", "❌ Overkill", "⚠️ Rarely needed"],
        "Why": [
            "Math errors compound without intermediate steps",
            "Skipped premises lead to wrong conclusions",
            "Dependencies must be identified first",
            "Bug source requires tracing execution",
            "Both sides must be weighed before deciding",
            "Single-step lookup, no reasoning needed",
            "Creativity is harmed by over-reasoning",
            "Pattern matching, not reasoning",
        ],
    })

    st.divider()
    st.markdown("#### CoT variants")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        with st.container(border=True):
            st.markdown("**Zero-shot CoT**")
            st.write("Add 'Let's think step by step.' — no examples needed.")
            st.code("...Let's think step by step:", language="text")

    with col_b:
        with st.container(border=True):
            st.markdown("**Few-shot CoT**")
            st.write("Provide 2–3 worked examples that show reasoning traces.")
            st.code("Q: ... A: Step 1... Step 2... Answer:", language="text")

    with col_c:
        with st.container(border=True):
            st.markdown("**Self-consistency**")
            st.write("Run CoT multiple times, take the majority answer (advanced).")
            st.code("Run N=5, vote on final answer", language="text")

    st.divider()
    st.success(
        "**UC3 — Structured Output:** CoT improves reasoning quality. "
        "Structured Output improves *format* reliability — forcing JSON so downstream code can parse it every time."
    )
