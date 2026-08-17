"""UC2 — Playground: Interactive LLM-as-Judge scorer."""

import streamlit as st

from applications.llm_evaluation.services.llm_judge import (
    DEFAULT_CRITERIA,
    JudgeCriteria,
    JudgeConfig,
    run_llm_judge,
)
from applications.llm_evaluation.uc2.constants import JUDGE_HISTORY_KEY, JUDGE_RESULT_KEY
from applications.shared.groq_models import DEFAULT_MODEL, get_available_chat_models

_SAMPLE_Q = "Explain what gradient descent is and how it's used in machine learning."
_SAMPLE_A = (
    "Gradient descent is an optimisation algorithm used to minimise the loss function of a machine "
    "learning model. It works by iteratively moving in the direction of the steepest descent — "
    "the negative gradient — until it reaches a local minimum. At each step, the model parameters "
    "are updated by subtracting the gradient multiplied by a learning rate. The learning rate controls "
    "how large each step is. A smaller learning rate leads to more precise convergence but is slower; "
    "a larger rate converges faster but may overshoot. Variants include stochastic gradient descent (SGD), "
    "mini-batch gradient descent, and adaptive methods like Adam."
)
_SAMPLE_B = (
    "Gradient descent is a way to train neural networks. You compute gradients and update weights. "
    "It's one of the most popular optimisation techniques in deep learning. "
    "There are different types like SGD and Adam. The learning rate is an important hyperparameter. "
    "Too high and the model diverges, too low and it trains slowly. Most frameworks handle this automatically."
)


def _init() -> None:
    if JUDGE_HISTORY_KEY not in st.session_state:
        st.session_state[JUDGE_HISTORY_KEY] = []
    if "_groq_models_cache" not in st.session_state:
        st.session_state["_groq_models_cache"] = get_available_chat_models()


def render() -> None:
    st.subheader("🧪 Playground — LLM-as-Judge")
    _init()

    models = st.session_state["_groq_models_cache"]
    default_idx = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0
    model = st.selectbox("Judge model", models, index=default_idx, key="llmeval_uc2_pg_model")

    col_sample, _ = st.columns([1, 4])
    with col_sample:
        if st.button("Load sample data", use_container_width=True):
            st.session_state["llmeval_uc2_pg_q"] = _SAMPLE_Q
            st.session_state["llmeval_uc2_pg_a"] = _SAMPLE_A
            st.session_state["llmeval_uc2_pg_b"] = _SAMPLE_B
            st.rerun()

    question = st.text_area(
        "Question / Prompt",
        key="llmeval_uc2_pg_q",
        placeholder="What question or task did the LLM respond to?",
        height=70,
    )

    col_ra, col_rb = st.columns(2)
    with col_ra:
        response_a = st.text_area(
            "Response A",
            key="llmeval_uc2_pg_a",
            placeholder="First response to evaluate...",
            height=200,
        )
    with col_rb:
        response_b = st.text_area(
            "Response B",
            key="llmeval_uc2_pg_b",
            placeholder="Second response to evaluate...",
            height=200,
        )

    st.markdown("#### Evaluation Criteria")
    st.caption("All criteria from the default set are enabled. Uncheck to remove.")

    selected_criteria = []
    cols = st.columns(len(DEFAULT_CRITERIA))
    for i, c in enumerate(DEFAULT_CRITERIA):
        with cols[i]:
            if st.checkbox(c.name, value=True, key=f"llmeval_uc2_pg_crit_{c.name}"):
                selected_criteria.append(c)

    if not selected_criteria:
        st.warning("Select at least one criterion.")

    ready = all([question.strip(), response_a.strip(), response_b.strip(), selected_criteria])
    if st.button("Run Judge Evaluation", type="primary", disabled=not ready):
        config = JudgeConfig(llm_model=model, temperature=0.0)
        with st.spinner("Judge evaluating both responses…"):
            result = run_llm_judge(
                question.strip(),
                response_a.strip(),
                response_b.strip(),
                selected_criteria,
                config,
            )
        st.session_state[JUDGE_RESULT_KEY] = result
        st.session_state[JUDGE_HISTORY_KEY].append(result)
        st.rerun()

    result = st.session_state.get(JUDGE_RESULT_KEY)
    if result:
        st.divider()
        st.markdown("### Judge Verdict")

        if result.winner == "A":
            st.success(f"Response A wins — {result.overall_reasoning}")
        elif result.winner == "B":
            st.success(f"Response B wins — {result.overall_reasoning}")
        else:
            st.info(f"Tie — {result.overall_reasoning}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Response A Score", f"{result.weighted_avg_a:.1f}/10")
        c2.metric("Response B Score", f"{result.weighted_avg_b:.1f}/10")
        c3.metric("Winner", result.winner)

        st.markdown("### Scores by Criterion")
        for score_a, score_b in zip(result.scores_a, result.scores_b):
            with st.container(border=True):
                st.markdown(f"**{score_a.criterion}**")
                col_a_col, col_b_col = st.columns(2)
                with col_a_col:
                    bar_a = int(score_a.score / 10 * 100)
                    st.markdown(
                        f"A: **{score_a.score:.0f}/10**  "
                        f"<div style='background:#e0e0e0;border-radius:4px;height:10px;'>"
                        f"<div style='background:#2196F3;width:{bar_a}%;height:10px;border-radius:4px;'></div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    with st.expander("Reason A", expanded=False):
                        st.write(score_a.reasoning)
                with col_b_col:
                    bar_b = int(score_b.score / 10 * 100)
                    st.markdown(
                        f"B: **{score_b.score:.0f}/10**  "
                        f"<div style='background:#e0e0e0;border-radius:4px;height:10px;'>"
                        f"<div style='background:#FF9800;width:{bar_b}%;height:10px;border-radius:4px;'></div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    with st.expander("Reason B", expanded=False):
                        st.write(score_b.reasoning)

    history = st.session_state.get(JUDGE_HISTORY_KEY, [])
    if len(history) > 1:
        st.divider()
        st.markdown(f"#### Evaluation history ({len(history)} runs)")
        for i, h in enumerate(reversed(history), 1):
            label = h.response_a[:50] + "…"
            with st.expander(f"Run {len(history) - i + 1}: A={h.weighted_avg_a:.1f}, B={h.weighted_avg_b:.1f}, Winner={h.winner}"):
                st.caption(h.timestamp[:19] + "Z")
