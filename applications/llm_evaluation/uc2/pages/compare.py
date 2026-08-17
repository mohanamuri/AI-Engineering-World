"""UC2 — Compare: Run the same question through two models, then judge them."""

import streamlit as st

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from applications.llm_evaluation.services.llm_judge import (
    DEFAULT_CRITERIA,
    JudgeConfig,
    run_llm_judge,
)
from applications.shared.groq_models import DEFAULT_MODEL, get_available_chat_models


def _init() -> None:
    if "_groq_models_cache" not in st.session_state:
        st.session_state["_groq_models_cache"] = get_available_chat_models()


def _generate_response(model: str, system_prompt: str, question: str) -> str:
    """Call the specified model and return its response text."""
    import os
    try:
        import streamlit as st
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY", "")
    llm = ChatGroq(model=model, temperature=0.3, api_key=api_key)
    resp = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=question),
    ])
    return resp.content.strip()


def render() -> None:
    st.subheader("⚖️ Compare — Two Models Judged Side by Side")
    _init()

    st.markdown(
        "Generate responses to the same question using two different models, "
        "then use the judge LLM to score and compare them. "
        "This workflow is how you decide which model to use in production."
    )

    models = st.session_state["_groq_models_cache"]
    default_idx = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        model_a = st.selectbox("Model A (generator)", models, index=default_idx, key="llmeval_uc2_cmp_ma")
    with col_m2:
        model_b = st.selectbox("Model B (generator)", models,
                               index=min(default_idx + 1, len(models) - 1),
                               key="llmeval_uc2_cmp_mb")

    judge_model = st.selectbox("Judge model", models, index=default_idx, key="llmeval_uc2_cmp_judge")

    system_prompt = st.text_area(
        "System prompt (used for both generators)",
        value="You are a helpful assistant. Answer concisely and accurately.",
        key="llmeval_uc2_cmp_sys",
        height=80,
    )

    question = st.text_area(
        "Question",
        key="llmeval_uc2_cmp_q",
        placeholder="e.g. What are the main differences between supervised and unsupervised learning?",
        height=80,
    )

    if st.button("Generate + Judge", type="primary", disabled=not question.strip()):
        with st.spinner(f"Generating response from {model_a}…"):
            resp_a = _generate_response(model_a, system_prompt, question.strip())
        with st.spinner(f"Generating response from {model_b}…"):
            resp_b = _generate_response(model_b, system_prompt, question.strip())

        with st.spinner("Judge evaluating both responses…"):
            config = JudgeConfig(llm_model=judge_model, temperature=0.0)
            judge_result = run_llm_judge(
                question.strip(), resp_a, resp_b, DEFAULT_CRITERIA, config
            )

        st.session_state["llmeval_uc2_cmp_resp_a"] = resp_a
        st.session_state["llmeval_uc2_cmp_resp_b"] = resp_b
        st.session_state["llmeval_uc2_cmp_judge_result"] = judge_result
        st.rerun()

    resp_a = st.session_state.get("llmeval_uc2_cmp_resp_a")
    resp_b = st.session_state.get("llmeval_uc2_cmp_resp_b")
    judge_result = st.session_state.get("llmeval_uc2_cmp_judge_result")

    if resp_a and resp_b and judge_result:
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Model A: `{model_a}`**")
            with st.container(border=True):
                st.write(resp_a)
        with col_b:
            st.markdown(f"**Model B: `{model_b}`**")
            with st.container(border=True):
                st.write(resp_b)

        st.divider()
        st.markdown("### Judge Scores")

        if judge_result.winner == "A":
            st.success(f"Model A ({model_a}) wins — {judge_result.overall_reasoning}")
        elif judge_result.winner == "B":
            st.success(f"Model B ({model_b}) wins — {judge_result.overall_reasoning}")
        else:
            st.info(f"Tie — {judge_result.overall_reasoning}")

        header = st.columns([2, 1, 1])
        header[0].markdown("**Criterion**")
        header[1].markdown(f"**{model_a}**")
        header[2].markdown(f"**{model_b}**")

        for sa, sb in zip(judge_result.scores_a, judge_result.scores_b):
            row = st.columns([2, 1, 1])
            row[0].markdown(sa.criterion)
            row[1].markdown(f"{sa.score:.0f}/10")
            row[2].markdown(f"{sb.score:.0f}/10")

        overall_row = st.columns([2, 1, 1])
        overall_row[0].markdown("**Weighted Average**")
        overall_row[1].markdown(f"**{judge_result.weighted_avg_a:.1f}/10**")
        overall_row[2].markdown(f"**{judge_result.weighted_avg_b:.1f}/10**")

        st.divider()
        st.markdown("### What to do with these results")
        st.markdown(
            "- If Model A wins consistently across multiple questions → use Model A in production\n"
            "- If it's a tie → choose the cheaper or faster model\n"
            "- If criteria scores differ (one model is more accurate but less clear) → "
            "decide which criterion matters most for your use case and weight it higher\n"
            "- Re-run with a different system prompt to see if the gap narrows"
        )
