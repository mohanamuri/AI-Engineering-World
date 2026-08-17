"""UC4 — Playground: Run full eval pipeline on a test dataset."""

import json

import streamlit as st

from applications.llm_evaluation.services.eval_pipeline import (
    PipelineConfig,
    TestCase,
    run_eval_pipeline,
)
from applications.llm_evaluation.uc4.constants import PIPELINE_RESULT_KEY
from applications.shared.groq_models import DEFAULT_MODEL, get_available_chat_models

_SAMPLE_CASES = [
    {
        "question": "What documents are required to open a business bank account?",
        "answer": (
            "To open a business bank account, you typically need: a government-issued ID, "
            "your business registration certificate, an EIN (Employer Identification Number), "
            "and the business's operating agreement or articles of incorporation. "
            "Some banks may also require a minimum opening deposit."
        ),
        "contexts": [
            "Requirements for opening a business bank account: (1) Valid government-issued "
            "photo ID for all account signatories. (2) Business registration certificate or "
            "articles of incorporation. (3) Employer Identification Number (EIN) issued by the IRS. "
            "(4) Business operating agreement (for LLCs) or corporate bylaws (for corporations). "
            "(5) Minimum opening deposit varies by bank.",
            "Some financial institutions may require additional documentation such as a business "
            "license from your state or local authority.",
        ],
        "ground_truth": (
            "Government-issued ID, business registration certificate, EIN, operating agreement "
            "or articles of incorporation, and a minimum opening deposit."
        ),
    },
    {
        "question": "How does the body regulate blood sugar levels?",
        "answer": (
            "Blood sugar is regulated primarily by the pancreas, which produces insulin and glucagon. "
            "When blood glucose rises after eating, the pancreas releases insulin, which allows cells "
            "to absorb glucose for energy. When blood sugar falls too low, glucagon signals the liver "
            "to release stored glucose. This feedback loop maintains glucose within a normal range "
            "of approximately 70–140 mg/dL."
        ),
        "contexts": [
            "The pancreas plays a central role in blood glucose regulation. Beta cells in the "
            "islets of Langerhans produce insulin, which facilitates cellular uptake of glucose. "
            "Alpha cells produce glucagon, which stimulates hepatic glucose release when blood "
            "sugar is low.",
            "Normal fasting blood glucose levels range from 70 to 100 mg/dL. Postprandial "
            "(after-meal) glucose may reach up to 140 mg/dL in healthy individuals.",
        ],
        "ground_truth": (
            "The pancreas regulates blood sugar via insulin (lowers glucose) and glucagon "
            "(raises glucose). Normal range: 70–100 mg/dL fasting."
        ),
    },
    {
        "question": "What is the difference between supervised and unsupervised learning?",
        "answer": (
            "Supervised learning uses labelled training data — each example has an input and a "
            "known correct output. The model learns to map inputs to outputs (e.g., email spam "
            "classification). Unsupervised learning uses unlabelled data and the model finds "
            "patterns or structure on its own (e.g., customer segmentation via clustering). "
            "The key difference is whether labels are provided during training."
        ),
        "contexts": [
            "In supervised learning, a dataset of input-output pairs is used to train a model. "
            "Common tasks include classification (predicting a category) and regression "
            "(predicting a continuous value). Examples include image classification and price prediction.",
            "Unsupervised learning algorithms find patterns in data without labelled responses. "
            "Common techniques include k-means clustering, hierarchical clustering, and "
            "dimensionality reduction methods such as PCA.",
        ],
        "ground_truth": (
            "Supervised: uses labelled data to learn input→output mappings. "
            "Unsupervised: finds patterns in unlabelled data. "
            "Key difference: presence of labels during training."
        ),
    },
]


def _init() -> None:
    if "_groq_models_cache" not in st.session_state:
        st.session_state["_groq_models_cache"] = get_available_chat_models()


def _score_badge(score: float, threshold: float = 0.70) -> str:
    if score >= threshold:
        return f"🟢 {score:.2f}"
    elif score >= threshold - 0.15:
        return f"🟡 {score:.2f}"
    else:
        return f"🔴 {score:.2f}"


def render() -> None:
    st.subheader("🧪 Playground — Eval Pipeline")
    _init()

    models = st.session_state["_groq_models_cache"]
    default_idx = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0
    model = st.selectbox("Model", models, index=default_idx, key="llmeval_uc4_pg_model")

    st.markdown("#### Pipeline Configuration")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        run_ragas = st.checkbox("Run RAGAS evaluation", value=True, key="llmeval_uc4_pg_ragas")
    with col_c2:
        run_hallucination = st.checkbox("Run hallucination detection", value=True, key="llmeval_uc4_pg_hall")

    st.markdown("#### Test Dataset")
    data_source = st.radio(
        "Data source",
        ["Use 3 built-in sample test cases", "Upload JSON file"],
        key="llmeval_uc4_pg_source",
        horizontal=True,
    )

    test_cases: list[TestCase] = []

    if data_source == "Use 3 built-in sample test cases":
        st.info(f"3 sample test cases loaded: business banking, blood sugar regulation, ML fundamentals.")
        test_cases = [
            TestCase(
                question=tc["question"],
                answer=tc["answer"],
                contexts=tc["contexts"],
                ground_truth=tc["ground_truth"],
            )
            for tc in _SAMPLE_CASES
        ]
        st.markdown("**Preview:**")
        for i, tc in enumerate(test_cases, 1):
            with st.expander(f"Case {i}: {tc.question[:60]}…"):
                st.markdown(f"**Answer:** {tc.answer[:200]}…")
                st.markdown(f"**Contexts:** {len(tc.contexts)} chunk(s)")
    else:
        uploaded = st.file_uploader("Upload test cases JSON", type=["json"])
        if uploaded:
            try:
                data = json.load(uploaded)
                test_cases = [
                    TestCase(
                        question=tc["question"],
                        answer=tc["answer"],
                        contexts=tc.get("contexts", []),
                        ground_truth=tc.get("ground_truth", ""),
                        reference_answer=tc.get("reference_answer", ""),
                    )
                    for tc in data
                ]
                st.success(f"Loaded {len(test_cases)} test cases from JSON.")
            except Exception as e:
                st.error(f"Could not parse JSON: {e}")

    if not (run_ragas or run_hallucination):
        st.warning("Select at least one evaluation to run.")

    ready = test_cases and (run_ragas or run_hallucination)
    if st.button("Run Eval Pipeline", type="primary", disabled=not ready):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def progress_cb(done: int, total: int) -> None:
            progress_bar.progress(done / total)
            status_text.caption(f"Evaluating case {done} of {total}…")

        config = PipelineConfig(
            llm_model=model,
            temperature=0.0,
            run_ragas=run_ragas,
            run_hallucination=run_hallucination,
        )
        pipeline_result = run_eval_pipeline(test_cases, config, progress_cb=progress_cb)
        progress_bar.progress(1.0)
        status_text.caption("Done.")
        st.session_state[PIPELINE_RESULT_KEY] = pipeline_result
        st.rerun()

    result = st.session_state.get(PIPELINE_RESULT_KEY)
    if result:
        st.divider()
        st.markdown("### Metrics Dashboard")

        if run_ragas or result.avg_overall > 0:
            st.markdown("#### RAGAS Averages")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Faithfulness", _score_badge(result.avg_faithfulness))
            c2.metric("Relevance", _score_badge(result.avg_relevance))
            c3.metric("Recall", _score_badge(result.avg_recall))
            c4.metric("Precision", _score_badge(result.avg_precision))
            c5.metric("Overall", _score_badge(result.avg_overall))

        if run_hallucination or result.avg_hallucination_rate > 0:
            st.markdown("#### Hallucination")
            hall_badge = (
                "🟢" if result.avg_hallucination_rate < 0.20
                else "🟡" if result.avg_hallucination_rate < 0.40
                else "🔴"
            )
            st.metric("Avg Hallucination Rate", f"{hall_badge} {result.avg_hallucination_rate:.0%}")

        st.markdown("#### Per-Case Results")
        for i, case_result in enumerate(result.cases, 1):
            tc = case_result.test_case
            question_preview = tc.question[:60] + ("…" if len(tc.question) > 60 else "")
            ragas_label = ""
            hall_label = ""
            if case_result.ragas:
                ragas_label = f"RAGAS: {case_result.ragas.overall_score:.2f}"
            if case_result.hallucination:
                hall_label = f"Hall: {case_result.hallucination.hallucination_rate:.0%} ({case_result.hallucination.overall_verdict})"

            header = f"Case {i}: {question_preview}"
            if ragas_label or hall_label:
                header += f"  —  {ragas_label}  {hall_label}"

            with st.expander(header):
                st.markdown(f"**Question:** {tc.question}")
                st.markdown(f"**Answer:** {tc.answer[:300]}{'…' if len(tc.answer) > 300 else ''}")

                if case_result.ragas:
                    r = case_result.ragas
                    rc1, rc2, rc3, rc4 = st.columns(4)
                    rc1.metric("Faithfulness", f"{r.faithfulness:.2f}")
                    rc2.metric("Relevance", f"{r.answer_relevance:.2f}")
                    rc3.metric("Recall", f"{r.context_recall:.2f}")
                    rc4.metric("Precision", f"{r.context_precision:.2f}")

                if case_result.hallucination:
                    h = case_result.hallucination
                    hc1, hc2 = st.columns(2)
                    hc1.metric("Hallucination rate", f"{h.hallucination_rate:.0%}")
                    hc2.metric("Verdict", h.overall_verdict)
                    supported = sum(1 for c in h.claims if c.verdict == "SUPPORTED")
                    contradicted = sum(1 for c in h.claims if c.verdict == "CONTRADICTED")
                    st.caption(f"{len(h.claims)} claims: {supported} supported, {contradicted} contradicted")
