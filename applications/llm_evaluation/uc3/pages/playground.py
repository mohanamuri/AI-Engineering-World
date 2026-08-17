"""UC3 — Playground: Interactive hallucination detection."""

import streamlit as st

from applications.llm_evaluation.services.hallucination import (
    HallucinationConfig,
    detect_hallucination,
)
from applications.llm_evaluation.uc3.constants import HALLUC_HISTORY_KEY, HALLUC_RESULT_KEY
from applications.shared.groq_models import DEFAULT_MODEL, get_available_chat_models

_SAMPLE_RESPONSE = (
    "The Great Barrier Reef is located off the coast of Queensland, Australia and is the world's "
    "largest coral reef system. It spans approximately 2,300 kilometres and was declared a UNESCO "
    "World Heritage Site in 1981. The reef is home to over 1,500 species of fish and more than "
    "600 types of coral. Unfortunately, due to rising ocean temperatures caused by climate change, "
    "the reef has experienced widespread bleaching events since the 1970s, with the most severe "
    "occurring in 2016 and 2017. Scientists estimate that 50% of the reef's coral has been lost "
    "since the 1995."
)

_SAMPLE_CONTEXT = (
    "The Great Barrier Reef is the world's largest coral reef system, located in the Coral Sea "
    "off the coast of Queensland, Australia. It stretches over 2,300 kilometres (1,400 miles) "
    "and covers an area of approximately 344,400 square kilometres. The reef was inscribed as a "
    "UNESCO World Heritage Site in 1981. It contains over 2,900 individual reefs and 900 islands. "
    "The reef supports an enormous diversity of life, including more than 1,500 species of fish "
    "and around 400 types of coral. Mass coral bleaching events occurred in 1998, 2002, 2016, "
    "2017, 2020, and 2022, driven by elevated sea surface temperatures. Studies suggest that "
    "between 2016 and 2022 approximately half of the reef's coral cover was lost."
)


def _init() -> None:
    if HALLUC_HISTORY_KEY not in st.session_state:
        st.session_state[HALLUC_HISTORY_KEY] = []
    if "_groq_models_cache" not in st.session_state:
        st.session_state["_groq_models_cache"] = get_available_chat_models()


def _verdict_badge(verdict: str) -> str:
    colors = {
        "SUPPORTED": ("🟢", "#4CAF50"),
        "CONTRADICTED": ("🔴", "#F44336"),
        "UNVERIFIABLE": ("🟡", "#FF9800"),
    }
    icon, _ = colors.get(verdict, ("⚪", "#9E9E9E"))
    return f"{icon} {verdict}"


def render() -> None:
    st.subheader("🧪 Playground — Hallucination Detection")
    _init()

    models = st.session_state["_groq_models_cache"]
    default_idx = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0
    model = st.selectbox("Model", models, index=default_idx, key="llmeval_uc3_pg_model")

    col_sample, _ = st.columns([1, 4])
    with col_sample:
        if st.button("Load sample data", use_container_width=True):
            st.session_state["llmeval_uc3_pg_resp"] = _SAMPLE_RESPONSE
            st.session_state["llmeval_uc3_pg_ctx"] = _SAMPLE_CONTEXT
            st.rerun()

    response = st.text_area(
        "LLM Response to check",
        key="llmeval_uc3_pg_resp",
        placeholder="Paste the LLM's response here — we'll extract and verify each claim...",
        height=180,
    )
    source_context = st.text_area(
        "Source context (the ground truth to verify against)",
        key="llmeval_uc3_pg_ctx",
        placeholder="Paste the authoritative source text here (retrieved documents, policy text, etc.)...",
        height=150,
    )

    ready = all([response.strip(), source_context.strip()])
    if st.button("Detect Hallucinations", type="primary", disabled=not ready):
        config = HallucinationConfig(llm_model=model, temperature=0.0)
        with st.spinner("Extracting and verifying claims…"):
            result = detect_hallucination(response.strip(), source_context.strip(), config)
        st.session_state[HALLUC_RESULT_KEY] = result
        st.session_state[HALLUC_HISTORY_KEY].append(result)
        st.rerun()

    result = st.session_state.get(HALLUC_RESULT_KEY)
    if result:
        st.divider()
        st.markdown("### Results")

        verdict_color = {
            "Low Risk": "success",
            "Medium Risk": "warning",
            "High Risk": "error",
        }[result.overall_verdict]

        c1, c2, c3 = st.columns(3)
        c1.metric("Claims extracted", len(result.claims))
        c2.metric("Hallucination rate", f"{result.hallucination_rate:.0%}")
        c3.metric("Overall verdict", result.overall_verdict)

        if result.overall_verdict == "Low Risk":
            st.success(f"Low Risk — {result.hallucination_rate:.0%} of claims are unsupported")
        elif result.overall_verdict == "Medium Risk":
            st.warning(f"Medium Risk — {result.hallucination_rate:.0%} of claims are unsupported. Review before publishing.")
        else:
            st.error(f"High Risk — {result.hallucination_rate:.0%} of claims are unsupported. Do not show to users.")

        st.markdown("### Claim-by-Claim Verification")

        supported = [c for c in result.claims if c.verdict == "SUPPORTED"]
        contradicted = [c for c in result.claims if c.verdict == "CONTRADICTED"]
        unverifiable = [c for c in result.claims if c.verdict == "UNVERIFIABLE"]

        if contradicted:
            st.markdown(f"#### 🔴 Contradicted ({len(contradicted)} claim{'s' if len(contradicted) > 1 else ''})")
            for cv in contradicted:
                with st.expander(f"❌ {cv.claim[:80]}{'…' if len(cv.claim) > 80 else ''}"):
                    st.markdown(f"**Verdict:** 🔴 CONTRADICTED (confidence: {cv.confidence:.0%})")
                    st.markdown(f"**Evidence:** {cv.evidence}")

        if unverifiable:
            st.markdown(f"#### 🟡 Unverifiable ({len(unverifiable)} claim{'s' if len(unverifiable) > 1 else ''})")
            for cv in unverifiable:
                with st.expander(f"⚠️ {cv.claim[:80]}{'…' if len(cv.claim) > 80 else ''}"):
                    st.markdown(f"**Verdict:** 🟡 UNVERIFIABLE (confidence: {cv.confidence:.0%})")
                    st.markdown(f"**Evidence:** {cv.evidence}")

        if supported:
            st.markdown(f"#### 🟢 Supported ({len(supported)} claim{'s' if len(supported) > 1 else ''})")
            for cv in supported:
                with st.expander(f"✅ {cv.claim[:80]}{'…' if len(cv.claim) > 80 else ''}"):
                    st.markdown(f"**Verdict:** 🟢 SUPPORTED (confidence: {cv.confidence:.0%})")
                    st.markdown(f"**Evidence:** {cv.evidence}")

    history = st.session_state.get(HALLUC_HISTORY_KEY, [])
    if len(history) > 1:
        st.divider()
        st.markdown(f"#### Detection history ({len(history)} runs)")
        for i, h in enumerate(reversed(history), 1):
            preview = h.response[:60] + "…"
            with st.expander(f"Run {len(history) - i + 1}: {h.overall_verdict} ({h.hallucination_rate:.0%}) — {preview}"):
                c1, c2 = st.columns(2)
                c1.metric("Claims", len(h.claims))
                c2.metric("Hall. rate", f"{h.hallucination_rate:.0%}")
                st.caption(h.timestamp[:19] + "Z")
