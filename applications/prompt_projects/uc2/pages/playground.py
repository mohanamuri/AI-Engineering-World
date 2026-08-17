"""UC2 — Playground page: try direct vs CoT interactively."""

import streamlit as st

from applications.prompt_projects.services.prompt_service import (
    PromptConfig,
    run_cot,
    run_direct,
)
from applications.prompt_projects.uc2.constants import (
    COT_RESULT_KEY,
    CONFIG_SESSION_KEY,
    DIRECT_RESULT_KEY,
    QUESTION_SESSION_KEY,
)

_SAMPLE_QUESTIONS = [
    "If I have 3 meetings of 45 minutes each and 2 hours of focus time, how long is my workday in hours?",
    "A train leaves at 9:00 AM travelling at 60 mph. Another leaves 30 minutes later at 80 mph. When does the second train catch up?",
    "Should a startup hire a generalist or a specialist first? Think through the trade-offs.",
    "A store sells apples for $0.50 and oranges for $0.75. I spend $5.25 and buy 9 fruits total. How many of each?",
]


def render() -> None:
    st.subheader("🧪 Playground")
    st.write("Enter a reasoning question and compare direct vs Chain-of-Thought output.")

    with st.expander("⚙️ Model settings", expanded=False):
        col1, col2 = st.columns(2)
        model = col1.selectbox("Model", ["meta-llama/llama-4-scout-17b-16e-instruct", "meta-llama/llama-4-maverick-17b-128e-instruct"], index=0, key="uc2_model")
        temperature = col2.slider("Temperature", 0.0, 1.0, 0.3, 0.1, key="uc2_temp",
                                   help="Lower temperature = more deterministic reasoning")
        config = PromptConfig(model=model, temperature=temperature)
        st.session_state[CONFIG_SESSION_KEY] = config

    config: PromptConfig = st.session_state.get(CONFIG_SESSION_KEY, PromptConfig(temperature=0.3))

    st.markdown("#### Your question")
    st.caption("Pick a sample or write your own reasoning/logic question:")
    cols = st.columns(2)
    for i, q in enumerate(_SAMPLE_QUESTIONS):
        if cols[i % 2].button(q, key=f"sample_uc2_{i}", use_container_width=True):
            st.session_state[QUESTION_SESSION_KEY] = q

    question = st.text_area(
        "Question",
        value=st.session_state.get(QUESTION_SESSION_KEY, ""),
        height=80,
        placeholder="e.g. A bat and ball cost $1.10. The bat costs $1 more. How much is the ball?",
        label_visibility="collapsed",
    )
    if question:
        st.session_state[QUESTION_SESSION_KEY] = question

    technique = st.radio(
        "Technique",
        ["Direct", "Chain-of-Thought"],
        horizontal=True,
        label_visibility="collapsed",
        key="uc2_technique_radio",
    )

    if st.button("▶ Run", type="primary", disabled=not question, use_container_width=True):
        with st.spinner(f"Running {technique}…"):
            try:
                if technique == "Direct":
                    result = run_direct(question, config)
                    st.session_state[DIRECT_RESULT_KEY] = result
                else:
                    result = run_cot(question, config)
                    st.session_state[COT_RESULT_KEY] = result
            except Exception as exc:
                st.error(f"Groq call failed: {exc}")
                return

        st.success(f"Done — {result.latency_ms:.0f} ms · {result.tokens_out} tokens out")
        st.markdown(f"**Output ({technique}):**")
        st.markdown(result.output)

        with st.expander("View full prompt sent to model", expanded=False):
            st.code(result.prompt_used, language="text")
