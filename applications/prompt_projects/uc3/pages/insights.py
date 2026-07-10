"""UC3 — Insights page: structured output best practices."""

import streamlit as st

from applications.prompt_projects.uc3.constants import FREEFORM_RESULT_KEY, STRUCTURED_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Structured Output")

    fr = st.session_state.get(FREEFORM_RESULT_KEY)
    sr = st.session_state.get(STRUCTURED_RESULT_KEY)

    if fr or sr:
        st.markdown("#### Your run metrics")
        c1, c2, c3, c4 = st.columns(4)
        if fr:
            c1.metric("Freeform latency", f"{fr.latency_ms:.0f} ms")
            c2.metric("Freeform tokens out", fr.tokens_out)
        if sr:
            c3.metric("Structured latency", f"{sr.latency_ms:.0f} ms")
            c4.metric("Structured tokens out", sr.tokens_out)
        st.divider()

    st.markdown("#### When to use structured output")
    st.table({
        "Use case": [
            "Data extraction pipeline",
            "API response to frontend",
            "Database ingestion",
            "Classification with fixed labels",
            "Dashboard metrics",
            "Human-read summary",
            "Creative writing",
        ],
        "Structured?": ["✅ Always", "✅ Always", "✅ Always", "✅ Always", "✅ Always", "⚠️ Optional", "❌ No"],
        "Reason": [
            "Downstream code needs exact fields",
            "Frontend expects typed response",
            "INSERT requires column mapping",
            "Labels must match enum values",
            "Charts need numeric fields",
            "Human can tolerate prose",
            "JSON breaks the creative flow",
        ],
    })

    st.divider()
    st.markdown("#### Schema design tips")
    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown("**✅ Good schema design**")
            st.markdown(
                "- Use descriptive field names (`summary`, not `s`)\n"
                "- Add inline hints: `'positive | neutral | negative'`\n"
                "- Keep schemas flat — avoid deep nesting\n"
                "- Use arrays for lists: `['item1', 'item2']`\n"
                "- Keep temperature ≤ 0.2 for reliable JSON"
            )

    with col_b:
        with st.container(border=True):
            st.markdown("**❌ Schema pitfalls**")
            st.markdown(
                "- Don't use ambiguous field names\n"
                "- Avoid optional fields (model may skip them)\n"
                "- Don't rely on field order\n"
                "- Don't use types the model can't infer (`datetime`, `UUID`)\n"
                "- Don't use high temperature — it produces malformed JSON"
            )

    st.divider()
    st.success(
        "**UC4 — Prompt Chaining:** Structured output controls the *shape* of one response. "
        "Prompt Chaining controls the *sequence* — breaking a complex task into a pipeline "
        "of simpler prompts where each step's output feeds the next."
    )
