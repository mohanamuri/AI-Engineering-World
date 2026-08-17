"""UC4 — Compare: Run the same test suite on two different RAG configurations."""

import json

import streamlit as st

from applications.llm_evaluation.services.eval_pipeline import (
    PipelineConfig,
    TestCase,
    run_eval_pipeline,
)
from applications.shared.groq_models import DEFAULT_MODEL, get_available_chat_models

_SAMPLE_CASES = [
    {
        "question": "What is photosynthesis?",
        "answer": "Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into glucose and oxygen using chlorophyll.",
        "contexts": [
            "Photosynthesis is a biological process used by plants, algae, and some bacteria to convert light energy — usually from the sun — into chemical energy stored in glucose. The overall reaction requires water and carbon dioxide as inputs and produces glucose and oxygen.",
            "Chlorophyll, the green pigment in plant leaves, absorbs light energy primarily from the blue and red parts of the spectrum and uses it to drive the photosynthetic reaction.",
        ],
        "ground_truth": "Plants use sunlight, water, and CO2 to produce glucose and oxygen via photosynthesis. Chlorophyll absorbs the light energy.",
    },
    {
        "question": "What causes inflation?",
        "answer": "Inflation is primarily caused by demand-pull factors (too much money chasing too few goods), cost-push factors (rising production costs), and built-in inflation from wage-price spirals.",
        "contexts": [
            "Demand-pull inflation occurs when aggregate demand in an economy exceeds aggregate supply, leading to price increases. This can be triggered by increased consumer spending, government stimulus, or low interest rates.",
            "Cost-push inflation arises when the costs of production increase, causing businesses to raise prices to maintain profit margins. Rising energy prices and raw material costs are common drivers.",
        ],
        "ground_truth": "Inflation is caused by demand-pull (excess demand), cost-push (rising production costs), or built-in wage-price spirals.",
    },
]


def _init() -> None:
    if "_groq_models_cache" not in st.session_state:
        st.session_state["_groq_models_cache"] = get_available_chat_models()


def render() -> None:
    st.subheader("⚖️ Compare — Two RAG Configurations on the Same Test Suite")
    _init()

    st.markdown(
        "Run the same test dataset through two different model configurations and compare "
        "their evaluation metrics side by side. This is the standard workflow for deciding "
        "whether a model or prompt change is a genuine improvement."
    )

    models = st.session_state["_groq_models_cache"]
    default_idx = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        model_a = st.selectbox("Configuration A model", models, index=default_idx, key="llmeval_uc4_cmp_ma")
    with col_m2:
        model_b = st.selectbox("Configuration B model", models,
                               index=min(default_idx + 1, len(models) - 1),
                               key="llmeval_uc4_cmp_mb")

    st.markdown("#### Pipeline Options")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        run_ragas = st.checkbox("Run RAGAS", value=True, key="llmeval_uc4_cmp_ragas")
    with col_c2:
        run_hallucination = st.checkbox("Run Hallucination Detection", value=True, key="llmeval_uc4_cmp_hall")

    data_source = st.radio(
        "Test data",
        ["Use 2 built-in sample cases", "Upload JSON"],
        key="llmeval_uc4_cmp_source",
        horizontal=True,
    )

    test_cases: list[TestCase] = []
    if data_source == "Use 2 built-in sample cases":
        test_cases = [
            TestCase(
                question=tc["question"],
                answer=tc["answer"],
                contexts=tc["contexts"],
                ground_truth=tc["ground_truth"],
            )
            for tc in _SAMPLE_CASES
        ]
        st.info(f"{len(test_cases)} sample test cases loaded.")
    else:
        uploaded = st.file_uploader("Upload test cases JSON", type=["json"], key="llmeval_uc4_cmp_upload")
        if uploaded:
            try:
                data = json.load(uploaded)
                test_cases = [
                    TestCase(
                        question=tc["question"],
                        answer=tc["answer"],
                        contexts=tc.get("contexts", []),
                        ground_truth=tc.get("ground_truth", ""),
                    )
                    for tc in data
                ]
                st.success(f"Loaded {len(test_cases)} test cases.")
            except Exception as e:
                st.error(f"Could not parse JSON: {e}")

    ready = test_cases and (run_ragas or run_hallucination)
    if st.button("Run Comparison", type="primary", disabled=not ready):
        config_a = PipelineConfig(llm_model=model_a, temperature=0.0, run_ragas=run_ragas, run_hallucination=run_hallucination)
        config_b = PipelineConfig(llm_model=model_b, temperature=0.0, run_ragas=run_ragas, run_hallucination=run_hallucination)

        pb = st.progress(0)
        total_steps = len(test_cases) * 2

        step = [0]

        def cb_a(done, total):
            step[0] = done
            pb.progress(step[0] / total_steps)

        def cb_b(done, total):
            step[0] = len(test_cases) + done
            pb.progress(step[0] / total_steps)

        with st.spinner(f"Running pipeline on Configuration A ({model_a})…"):
            result_a = run_eval_pipeline(test_cases, config_a, progress_cb=cb_a)
        with st.spinner(f"Running pipeline on Configuration B ({model_b})…"):
            result_b = run_eval_pipeline(test_cases, config_b, progress_cb=cb_b)

        pb.progress(1.0)
        st.session_state["llmeval_uc4_cmp_result_a"] = result_a
        st.session_state["llmeval_uc4_cmp_result_b"] = result_b
        st.rerun()

    result_a = st.session_state.get("llmeval_uc4_cmp_result_a")
    result_b = st.session_state.get("llmeval_uc4_cmp_result_b")

    if result_a and result_b:
        st.divider()
        st.markdown("### Metrics Comparison")

        if run_ragas:
            st.markdown("#### RAGAS Averages")
            metric_rows = [
                ("Faithfulness", result_a.avg_faithfulness, result_b.avg_faithfulness),
                ("Relevance", result_a.avg_relevance, result_b.avg_relevance),
                ("Context Recall", result_a.avg_recall, result_b.avg_recall),
                ("Context Precision", result_a.avg_precision, result_b.avg_precision),
                ("Overall RAGAS", result_a.avg_overall, result_b.avg_overall),
            ]
            header = st.columns([2, 1, 1, 1])
            header[0].markdown("**Metric**")
            header[1].markdown(f"**Config A** (`{model_a[:20]}`)")
            header[2].markdown(f"**Config B** (`{model_b[:20]}`)")
            header[3].markdown("**Winner**")

            for metric_name, va, vb in metric_rows:
                row = st.columns([2, 1, 1, 1])
                row[0].markdown(metric_name)
                row[1].markdown(f"{va:.2f}")
                row[2].markdown(f"{vb:.2f}")
                if abs(va - vb) < 0.03:
                    row[3].markdown("🟡 Tie")
                elif va > vb:
                    row[3].markdown("🟢 A")
                else:
                    row[3].markdown("🔵 B")

        if run_hallucination:
            st.markdown("#### Hallucination Rates")
            hc = st.columns([2, 1, 1, 1])
            hc[0].markdown("Avg Hallucination Rate")
            hc[1].markdown(f"{result_a.avg_hallucination_rate:.0%}")
            hc[2].markdown(f"{result_b.avg_hallucination_rate:.0%}")
            if abs(result_a.avg_hallucination_rate - result_b.avg_hallucination_rate) < 0.05:
                hc[3].markdown("🟡 Tie")
            elif result_a.avg_hallucination_rate < result_b.avg_hallucination_rate:
                hc[3].markdown("🟢 A (lower is better)")
            else:
                hc[3].markdown("🔵 B (lower is better)")

        st.divider()
        st.markdown("### Decision Guide")
        st.markdown(
            "- If Config A consistently wins on RAGAS metrics → use Config A in production\n"
            "- If Config A wins on faithfulness but B wins on relevance → check which matters more for your use case\n"
            "- If the winner depends on the question → segment your test set by topic and compare separately\n"
            "- A tie across all metrics → prefer the cheaper or faster configuration"
        )
