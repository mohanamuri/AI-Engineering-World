"""UC1 — Compare: Evaluate two different answers to the same question side by side."""

import streamlit as st

from applications.llm_evaluation.services.ragas_eval import RAGASConfig, run_ragas_eval
from applications.shared.groq_models import DEFAULT_MODEL, get_available_chat_models

_SAMPLE_Q = "What are the symptoms of type 2 diabetes?"
_SAMPLE_CTX = (
    "Type 2 diabetes symptoms often develop slowly and include: increased thirst, "
    "frequent urination, increased hunger, unintended weight loss, fatigue, blurred vision, "
    "slow-healing sores, and frequent infections. Some people have no symptoms initially.\n"
    "Risk factors include obesity, physical inactivity, family history, and age over 45."
)
_SAMPLE_GT = (
    "Symptoms include increased thirst, frequent urination, fatigue, blurred vision, "
    "slow-healing sores, and frequent infections. Some develop no early symptoms."
)
_SAMPLE_A = (
    "Type 2 diabetes symptoms include increased thirst, frequent urination, fatigue, "
    "blurred vision, and slow-healing sores. Some people have no symptoms at all initially. "
    "These symptoms often develop gradually over time."
)
_SAMPLE_B = (
    "Diabetes can cause many problems. You might feel tired or thirsty sometimes. "
    "It is a serious disease affecting millions of people worldwide and can lead to "
    "complications involving the kidneys, eyes, and cardiovascular system. "
    "Treatment involves lifestyle changes and possibly medication."
)


def _init() -> None:
    if "_groq_models_cache" not in st.session_state:
        st.session_state["_groq_models_cache"] = get_available_chat_models()


def _score_bar_mini(score: float, color: str) -> str:
    pct = int(score * 100)
    return (
        f"<div style='background:#e0e0e0;border-radius:4px;height:10px;margin:2px 0 6px 0;'>"
        f"<div style='background:{color};width:{pct}%;height:10px;border-radius:4px;'></div>"
        f"</div>"
    )


def render() -> None:
    st.subheader("⚖️ Compare — Side-by-Side RAGAS Evaluation")
    _init()

    st.markdown(
        "Evaluate two different answers to the same question. "
        "This is useful when comparing a baseline RAG response against an improved version, "
        "or when testing two different LLMs as generators."
    )

    models = st.session_state["_groq_models_cache"]
    default_idx = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0
    model = st.selectbox("Judge model", models, index=default_idx, key="llmeval_uc1_cmp_model")

    col_sample, _ = st.columns([1, 4])
    with col_sample:
        if st.button("Load sample data", use_container_width=True):
            st.session_state["llmeval_uc1_cmp_q"] = _SAMPLE_Q
            st.session_state["llmeval_uc1_cmp_ctx"] = _SAMPLE_CTX
            st.session_state["llmeval_uc1_cmp_gt"] = _SAMPLE_GT
            st.session_state["llmeval_uc1_cmp_a"] = _SAMPLE_A
            st.session_state["llmeval_uc1_cmp_b"] = _SAMPLE_B
            st.rerun()

    question = st.text_area("Question", key="llmeval_uc1_cmp_q", height=60,
                            placeholder="The question both answers respond to")
    contexts_raw = st.text_area("Retrieved context (shared for both answers)", key="llmeval_uc1_cmp_ctx",
                                height=130, placeholder="Paste the retrieved document chunks...")
    ground_truth = st.text_area("Ground truth answer", key="llmeval_uc1_cmp_gt", height=60,
                                placeholder="What the ideal answer should contain")

    col_a, col_b = st.columns(2)
    with col_a:
        answer_a = st.text_area("Answer A", key="llmeval_uc1_cmp_a", height=150,
                                placeholder="Paste first answer here...")
    with col_b:
        answer_b = st.text_area("Answer B", key="llmeval_uc1_cmp_b", height=150,
                                placeholder="Paste second answer here...")

    ready = all([question.strip(), contexts_raw.strip(), ground_truth.strip(),
                 answer_a.strip(), answer_b.strip()])
    if st.button("Compare RAGAS Scores", type="primary", disabled=not ready):
        contexts = [c.strip() for c in contexts_raw.split("\n") if c.strip()]
        config = RAGASConfig(llm_model=model, temperature=0.0)
        col_a_res, col_b_res = st.columns(2)

        with col_a_res:
            st.markdown("**Evaluating Answer A…**")
            with st.spinner("Running RAGAS for A…"):
                result_a = run_ragas_eval(question.strip(), answer_a.strip(), contexts, ground_truth.strip(), config)

        with col_b_res:
            st.markdown("**Evaluating Answer B…**")
            with st.spinner("Running RAGAS for B…"):
                result_b = run_ragas_eval(question.strip(), answer_b.strip(), contexts, ground_truth.strip(), config)

        st.session_state["llmeval_uc1_cmp_result_a"] = result_a
        st.session_state["llmeval_uc1_cmp_result_b"] = result_b
        st.rerun()

    result_a = st.session_state.get("llmeval_uc1_cmp_result_a")
    result_b = st.session_state.get("llmeval_uc1_cmp_result_b")

    if result_a and result_b:
        st.divider()
        st.markdown("### Results")

        metrics = [
            ("Faithfulness", result_a.faithfulness, result_b.faithfulness, "#2196F3"),
            ("Answer Relevance", result_a.answer_relevance, result_b.answer_relevance, "#4CAF50"),
            ("Context Recall", result_a.context_recall, result_b.context_recall, "#FF9800"),
            ("Context Precision", result_a.context_precision, result_b.context_precision, "#9C27B0"),
            ("Overall", result_a.overall_score, result_b.overall_score, "#F44336"),
        ]

        header_cols = st.columns([2, 1, 1, 1])
        header_cols[0].markdown("**Metric**")
        header_cols[1].markdown("**Answer A**")
        header_cols[2].markdown("**Answer B**")
        header_cols[3].markdown("**Winner**")

        for metric_name, score_a, score_b, color in metrics:
            row_cols = st.columns([2, 1, 1, 1])
            row_cols[0].markdown(f"{metric_name}")
            row_cols[1].markdown(
                f"{score_a:.2f} {_score_bar_mini(score_a, color)}",
                unsafe_allow_html=True,
            )
            row_cols[2].markdown(
                f"{score_b:.2f} {_score_bar_mini(score_b, color)}",
                unsafe_allow_html=True,
            )
            if abs(score_a - score_b) < 0.05:
                row_cols[3].markdown("🟡 Tie")
            elif score_a > score_b:
                row_cols[3].markdown("🟢 A")
            else:
                row_cols[3].markdown("🔵 B")

        st.divider()
        if result_a.overall_score > result_b.overall_score + 0.05:
            st.success(f"Answer A wins overall — {result_a.overall_score:.2f} vs {result_b.overall_score:.2f}")
        elif result_b.overall_score > result_a.overall_score + 0.05:
            st.success(f"Answer B wins overall — {result_b.overall_score:.2f} vs {result_a.overall_score:.2f}")
        else:
            st.info(f"Effectively tied — A: {result_a.overall_score:.2f}, B: {result_b.overall_score:.2f}")

        st.markdown("### Interpretation")
        st.markdown(
            "- A **higher Faithfulness** for one answer means it stayed closer to the retrieved context\n"
            "- A **higher Context Recall** means the shared context was better utilised by that answer\n"
            "- If both answers score similarly on Context metrics, the retriever is the bottleneck — "
            "not which answer you choose\n"
            "- Use this comparison when A/B testing different LLMs as generators or different prompt templates"
        )
