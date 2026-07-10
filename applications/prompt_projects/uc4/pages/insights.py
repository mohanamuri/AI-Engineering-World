"""UC4 — Insights page: when to chain and when not to."""

import streamlit as st

from applications.prompt_projects.uc4.constants import CHAIN_RESULT_KEY, SINGLE_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Prompt Chaining")

    sr = st.session_state.get(SINGLE_RESULT_KEY)
    cr = st.session_state.get(CHAIN_RESULT_KEY)

    if sr or cr:
        st.markdown("#### Your run metrics")
        c1, c2, c3, c4 = st.columns(4)
        if sr:
            c1.metric("Single latency", f"{sr.latency_ms:.0f} ms")
            c2.metric("Single tokens out", sr.tokens_out)
        if cr:
            c3.metric("Chain total latency", f"{cr.total_latency_ms:.0f} ms")
            c4.metric("Chain total tokens", cr.total_tokens_out)
        if sr and cr:
            overhead = cr.total_tokens_out - sr.tokens_out
            st.info(
                f"The chain used **{overhead} more output tokens** across its 3 steps. "
                "Each step is shallower than the full task but the combined output is typically richer."
            )
        st.divider()

    st.markdown("#### When chaining is worth the overhead")
    st.table({
        "Task": [
            "Long-form content (blog, report)",
            "Multi-step analysis",
            "Code generation + review",
            "Research + summarisation",
            "Simple Q&A",
            "Short classification",
            "Real-time chat response",
        ],
        "Chain?": ["✅ Yes", "✅ Yes", "✅ Yes", "✅ Yes", "❌ Overkill", "❌ Overkill", "❌ Too slow"],
        "Why": [
            "Structure + depth benefit from decomposition",
            "Each dimension needs full focus",
            "Generation and critique are separate concerns",
            "Research depth and summary clarity need separate passes",
            "Single step is sufficient and faster",
            "One prompt handles it, no decomposition needed",
            "Latency matters more than depth",
        ],
    })

    st.divider()
    st.markdown("#### Chaining patterns beyond Outline → Draft → Refine")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        with st.container(border=True):
            st.markdown("**Extract → Analyse**")
            st.write("Step 1 extracts facts. Step 2 analyses them. Useful for document processing.")

    with col_b:
        with st.container(border=True):
            st.markdown("**Generate → Critique → Revise**")
            st.write("Self-improvement loop. The critic step catches errors the generator missed.")

    with col_c:
        with st.container(border=True):
            st.markdown("**Classify → Route → Specialise**")
            st.write("First prompt classifies the input, then routes to a specialised prompt.")

    st.divider()
    st.markdown("#### The progression you've completed")
    st.success(
        "**UC1 — Zero/Few-shot:** Control *what examples* the model sees.\n\n"
        "**UC2 — Chain-of-Thought:** Control *how* the model reasons.\n\n"
        "**UC3 — Structured Output:** Control *what shape* the output takes.\n\n"
        "**UC4 — Prompt Chaining:** Control *the pipeline* of multiple prompts.\n\n"
        "Together, these four techniques cover the core of production prompt engineering."
    )
