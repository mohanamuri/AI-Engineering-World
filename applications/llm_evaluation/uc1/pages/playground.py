"""UC1 — Playground: Interactive RAGAS evaluation scorer."""

import streamlit as st

from applications.llm_evaluation.services.ragas_eval import RAGASConfig, run_ragas_eval
from applications.llm_evaluation.uc1.constants import RAGAS_HISTORY_KEY, RAGAS_RESULT_KEY
from applications.shared.groq_models import DEFAULT_MODEL, get_available_chat_models

_SAMPLE_QUESTION = "What is the return policy for electronics purchased at the store?"
_SAMPLE_ANSWER = (
    "Electronics can be returned within 30 days of purchase with the original receipt. "
    "Items must be in original packaging and unopened. Opened software and digital downloads "
    "are non-refundable. Extended warranty plans are available for an additional fee."
)
_SAMPLE_CONTEXTS = [
    "Our return policy allows customers to return most items within 30 days of the original "
    "purchase date. A valid receipt is required for all returns.",
    "Electronics must be returned in their original, unopened packaging. Once the seal is broken, "
    "the item may only be exchanged for the same model if defective.",
    "Software, games, and digital download cards are non-refundable once opened or redeemed.",
]
_SAMPLE_GROUND_TRUTH = (
    "Electronics can be returned within 30 days with receipt. Must be unopened. "
    "Software and digital downloads are non-refundable."
)


def _init() -> None:
    if RAGAS_HISTORY_KEY not in st.session_state:
        st.session_state[RAGAS_HISTORY_KEY] = []
    if "_groq_models_cache" not in st.session_state:
        st.session_state["_groq_models_cache"] = get_available_chat_models()


def _score_bar(label: str, score: float, color: str) -> None:
    pct = int(score * 100)
    st.markdown(
        f"**{label}**: {score:.2f}  "
        f"<div style='background:#e0e0e0;border-radius:4px;height:12px;margin-bottom:6px;'>"
        f"<div style='background:{color};width:{pct}%;height:12px;border-radius:4px;'></div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render() -> None:
    st.subheader("🧪 Playground — RAGAS Evaluation")
    _init()

    models = st.session_state["_groq_models_cache"]
    default_idx = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0
    model = st.selectbox("Judge model", models, index=default_idx, key="llmeval_uc1_pg_model")

    col_sample, _ = st.columns([1, 4])
    with col_sample:
        if st.button("Load sample data", use_container_width=True):
            st.session_state["llmeval_uc1_pg_q"] = _SAMPLE_QUESTION
            st.session_state["llmeval_uc1_pg_a"] = _SAMPLE_ANSWER
            st.session_state["llmeval_uc1_pg_ctx"] = "\n".join(_SAMPLE_CONTEXTS)
            st.session_state["llmeval_uc1_pg_gt"] = _SAMPLE_GROUND_TRUTH
            st.rerun()

    question = st.text_area(
        "Question",
        key="llmeval_uc1_pg_q",
        placeholder="e.g. What is the return policy for electronics?",
        height=70,
    )
    answer = st.text_area(
        "RAG-generated answer (the response to evaluate)",
        key="llmeval_uc1_pg_a",
        placeholder="Paste the answer your RAG system produced...",
        height=110,
    )
    contexts_raw = st.text_area(
        "Retrieved context passages (one per line, or separated by blank lines)",
        key="llmeval_uc1_pg_ctx",
        placeholder="Paste the retrieved document chunks here...",
        height=150,
    )
    ground_truth = st.text_area(
        "Ground truth answer (for Context Recall metric)",
        key="llmeval_uc1_pg_gt",
        placeholder="What should the ideal answer look like?",
        height=70,
    )

    ready = all([question.strip(), answer.strip(), contexts_raw.strip(), ground_truth.strip()])
    if st.button("Run RAGAS Evaluation", type="primary", disabled=not ready):
        contexts = [c.strip() for c in contexts_raw.split("\n") if c.strip()]
        config = RAGASConfig(llm_model=model, temperature=0.0)
        with st.spinner("Evaluating all 4 RAGAS metrics…"):
            result = run_ragas_eval(question.strip(), answer.strip(), contexts, ground_truth.strip(), config)
        st.session_state[RAGAS_RESULT_KEY] = result
        st.session_state[RAGAS_HISTORY_KEY].append(result)
        st.rerun()

    result = st.session_state.get(RAGAS_RESULT_KEY)
    if result:
        st.divider()
        st.markdown("### RAGAS Scores")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Faithfulness", f"{result.faithfulness:.2f}")
        c2.metric("Answer Relevance", f"{result.answer_relevance:.2f}")
        c3.metric("Context Recall", f"{result.context_recall:.2f}")
        c4.metric("Context Precision", f"{result.context_precision:.2f}")
        c5.metric("Overall", f"{result.overall_score:.2f}")

        with st.container(border=True):
            _score_bar("Faithfulness", result.faithfulness, "#2196F3")
            _score_bar("Answer Relevance", result.answer_relevance, "#4CAF50")
            _score_bar("Context Recall", result.context_recall, "#FF9800")
            _score_bar("Context Precision", result.context_precision, "#9C27B0")

        st.markdown("### Judge Reasoning")
        with st.expander("Faithfulness reasoning"):
            st.write(result.faithfulness_reason)
        with st.expander("Answer Relevance reasoning"):
            st.write(result.relevance_reason)
        with st.expander("Context Recall reasoning"):
            st.write(result.recall_reason)
        with st.expander("Context Precision reasoning"):
            st.write(result.precision_reason)

        # Diagnosis
        diagnoses = []
        if result.faithfulness < 0.6:
            diagnoses.append("⚠️ **Low Faithfulness** — the LLM may be adding facts not in the context. Try a stricter system prompt or a different model.")
        if result.answer_relevance < 0.6:
            diagnoses.append("⚠️ **Low Answer Relevance** — the answer is off-topic. Check your prompt template and query handling.")
        if result.context_recall < 0.6:
            diagnoses.append("⚠️ **Low Context Recall** — the retriever may have missed important documents. Try increasing k or refining embeddings.")
        if result.context_precision < 0.6:
            diagnoses.append("⚠️ **Low Context Precision** — too many irrelevant documents retrieved. Reduce k or raise the similarity threshold.")
        if diagnoses:
            st.divider()
            st.markdown("### Diagnosis")
            for d in diagnoses:
                st.warning(d)
        else:
            st.success("All scores look healthy! Overall RAGAS score is strong.")

    history = st.session_state.get(RAGAS_HISTORY_KEY, [])
    if history:
        st.divider()
        st.markdown(f"#### Evaluation history ({len(history)} run{'s' if len(history) > 1 else ''})")
        for i, h in enumerate(reversed(history), 1):
            label = h.question[:60] + ("…" if len(h.question) > 60 else "")
            with st.expander(f"Run {len(history) - i + 1}: {label}"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Faithfulness", f"{h.faithfulness:.2f}")
                c2.metric("Relevance", f"{h.answer_relevance:.2f}")
                c3.metric("Recall", f"{h.context_recall:.2f}")
                c4.metric("Precision", f"{h.context_precision:.2f}")
                st.caption(f"Overall: {h.overall_score:.2f} · {h.timestamp[:19]}Z")
