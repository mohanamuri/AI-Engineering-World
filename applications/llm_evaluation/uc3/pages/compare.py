"""UC3 — Compare: Compare hallucination rate of two different responses to same source."""

import streamlit as st

from applications.llm_evaluation.services.hallucination import (
    HallucinationConfig,
    detect_hallucination,
)
from applications.shared.groq_models import DEFAULT_MODEL, get_available_chat_models

_SAMPLE_CTX = (
    "Python was created by Guido van Rossum and first released in 1991. "
    "It is an interpreted, high-level, general-purpose programming language. "
    "Python's design philosophy emphasises code readability with significant indentation. "
    "Python 3.0 was released in 2008 and is not fully backwards compatible with Python 2. "
    "Python 2 reached end-of-life on January 1, 2020. "
    "As of 2024, Python consistently ranks as one of the most popular programming languages worldwide."
)

_SAMPLE_A = (
    "Python is a high-level programming language created by Guido van Rossum, first released in 1991. "
    "It emphasises code readability and uses indentation to define code blocks. "
    "Python 3, released in 2008, is not fully backwards compatible with Python 2, "
    "which reached end-of-life in 2020."
)

_SAMPLE_B = (
    "Python was developed at MIT in the early 1990s by Guido van Rossum. It was first released in 1994. "
    "Python is known for being easy to learn and is widely used in data science. "
    "Python 3 was a major overhaul released in 2010 that broke many Python 2 programs. "
    "Python 2 is still widely used in enterprise applications today."
)


def _init() -> None:
    if "_groq_models_cache" not in st.session_state:
        st.session_state["_groq_models_cache"] = get_available_chat_models()


def render() -> None:
    st.subheader("⚖️ Compare — Hallucination Rate: Response A vs Response B")
    _init()

    st.markdown(
        "Compare the hallucination rate of two different responses to the same source context. "
        "Use this to evaluate which response is more factually grounded — "
        "for example, when comparing two different prompt templates or generator models."
    )

    models = st.session_state["_groq_models_cache"]
    default_idx = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0
    model = st.selectbox("Verifier model", models, index=default_idx, key="llmeval_uc3_cmp_model")

    col_sample, _ = st.columns([1, 4])
    with col_sample:
        if st.button("Load sample data", use_container_width=True):
            st.session_state["llmeval_uc3_cmp_ctx"] = _SAMPLE_CTX
            st.session_state["llmeval_uc3_cmp_a"] = _SAMPLE_A
            st.session_state["llmeval_uc3_cmp_b"] = _SAMPLE_B
            st.rerun()

    source_context = st.text_area(
        "Source context (shared — the authoritative text to verify against)",
        key="llmeval_uc3_cmp_ctx",
        height=140,
        placeholder="Paste the source document or policy text here...",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        response_a = st.text_area(
            "Response A",
            key="llmeval_uc3_cmp_a",
            height=200,
            placeholder="First response to check...",
        )
    with col_b:
        response_b = st.text_area(
            "Response B",
            key="llmeval_uc3_cmp_b",
            height=200,
            placeholder="Second response to check...",
        )

    ready = all([source_context.strip(), response_a.strip(), response_b.strip()])
    if st.button("Compare Hallucination Rates", type="primary", disabled=not ready):
        config = HallucinationConfig(llm_model=model, temperature=0.0)
        with st.spinner("Checking Response A…"):
            result_a = detect_hallucination(response_a.strip(), source_context.strip(), config)
        with st.spinner("Checking Response B…"):
            result_b = detect_hallucination(response_b.strip(), source_context.strip(), config)
        st.session_state["llmeval_uc3_cmp_result_a"] = result_a
        st.session_state["llmeval_uc3_cmp_result_b"] = result_b
        st.rerun()

    result_a = st.session_state.get("llmeval_uc3_cmp_result_a")
    result_b = st.session_state.get("llmeval_uc3_cmp_result_b")

    if result_a and result_b:
        st.divider()
        st.markdown("### Comparison")

        col_ra, col_rb = st.columns(2)
        with col_ra:
            with st.container(border=True):
                st.markdown("**Response A**")
                st.metric("Hallucination Rate", f"{result_a.hallucination_rate:.0%}")
                st.metric("Verdict", result_a.overall_verdict)
                st.metric("Claims extracted", len(result_a.claims))
                contradicted_a = sum(1 for c in result_a.claims if c.verdict == "CONTRADICTED")
                unverif_a = sum(1 for c in result_a.claims if c.verdict == "UNVERIFIABLE")
                st.caption(f"🔴 {contradicted_a} contradicted · 🟡 {unverif_a} unverifiable")
        with col_rb:
            with st.container(border=True):
                st.markdown("**Response B**")
                st.metric("Hallucination Rate", f"{result_b.hallucination_rate:.0%}")
                st.metric("Verdict", result_b.overall_verdict)
                st.metric("Claims extracted", len(result_b.claims))
                contradicted_b = sum(1 for c in result_b.claims if c.verdict == "CONTRADICTED")
                unverif_b = sum(1 for c in result_b.claims if c.verdict == "UNVERIFIABLE")
                st.caption(f"🔴 {contradicted_b} contradicted · 🟡 {unverif_b} unverifiable")

        st.divider()
        if result_a.hallucination_rate < result_b.hallucination_rate - 0.05:
            st.success(
                f"Response A is more factually grounded ({result_a.hallucination_rate:.0%} vs {result_b.hallucination_rate:.0%})"
            )
        elif result_b.hallucination_rate < result_a.hallucination_rate - 0.05:
            st.success(
                f"Response B is more factually grounded ({result_b.hallucination_rate:.0%} vs {result_a.hallucination_rate:.0%})"
            )
        else:
            st.info(
                f"Similar hallucination rates — A: {result_a.hallucination_rate:.0%}, B: {result_b.hallucination_rate:.0%}"
            )

        st.markdown("### Detailed Claims")
        col_da, col_db = st.columns(2)
        with col_da:
            st.markdown("**Response A — All Claims**")
            for cv in result_a.claims:
                badge = {"SUPPORTED": "🟢", "CONTRADICTED": "🔴", "UNVERIFIABLE": "🟡"}.get(cv.verdict, "⚪")
                with st.expander(f"{badge} {cv.claim[:60]}{'…' if len(cv.claim) > 60 else ''}"):
                    st.write(cv.evidence)
        with col_db:
            st.markdown("**Response B — All Claims**")
            for cv in result_b.claims:
                badge = {"SUPPORTED": "🟢", "CONTRADICTED": "🔴", "UNVERIFIABLE": "🟡"}.get(cv.verdict, "⚪")
                with st.expander(f"{badge} {cv.claim[:60]}{'…' if len(cv.claim) > 60 else ''}"):
                    st.write(cv.evidence)
