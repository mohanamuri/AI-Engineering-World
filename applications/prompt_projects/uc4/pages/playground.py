"""UC4 — Playground page: run the prompt chain interactively."""

import streamlit as st

from applications.prompt_projects.services.prompt_service import (
    PromptConfig,
    run_chain,
    run_single_prompt,
)
from applications.prompt_projects.uc4.constants import (
    CHAIN_RESULT_KEY,
    CONFIG_SESSION_KEY,
    SINGLE_RESULT_KEY,
    TASK_SESSION_KEY,
)

_SAMPLE_TASKS = [
    "Write a blog post about how AI is changing software development.",
    "Create a project plan for building a customer feedback analysis system.",
    "Write a technical explanation of how vector databases work.",
    "Produce a competitive analysis of cloud providers for a startup.",
]


def render() -> None:
    st.subheader("🧪 Playground")
    st.write("Enter a complex task and run it as a single prompt or as a three-step chain.")

    with st.expander("⚙️ Model settings", expanded=False):
        col1, col2 = st.columns(2)
        model = col1.selectbox("Model", ["gemma2-9b-it", "qwen/qwen3-32b", "moonshotai/kimi-k2-instruct"], index=0, key="uc4_model")
        temperature = col2.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="uc4_temp")
        config = PromptConfig(model=model, temperature=temperature)
        st.session_state[CONFIG_SESSION_KEY] = config

    config: PromptConfig = st.session_state.get(CONFIG_SESSION_KEY, PromptConfig())

    st.markdown("#### Task")
    cols = st.columns(2)
    for i, s in enumerate(_SAMPLE_TASKS):
        if cols[i % 2].button(s, key=f"sample_uc4_{i}", use_container_width=True):
            st.session_state[TASK_SESSION_KEY] = s

    task = st.text_area(
        "Task",
        value=st.session_state.get(TASK_SESSION_KEY, ""),
        height=80,
        placeholder="e.g. Write a blog post about AI in healthcare.",
        label_visibility="collapsed",
    )
    if task:
        st.session_state[TASK_SESSION_KEY] = task

    technique = st.radio(
        "Technique",
        ["Single Prompt", "Chain (Outline → Draft → Refine)"],
        horizontal=True,
        label_visibility="collapsed",
        key="uc4_technique_radio",
    )

    if st.button("▶ Run", type="primary", disabled=not task, use_container_width=True):
        if technique == "Single Prompt":
            with st.spinner("Running single prompt…"):
                try:
                    result = run_single_prompt(task, config)
                    st.session_state[SINGLE_RESULT_KEY] = result
                except Exception as exc:
                    st.error(f"Failed: {exc}")
                    return
            st.success(f"Done — {result.latency_ms:.0f} ms · {result.tokens_out} tokens")
            st.markdown("**Output:**")
            st.markdown(result.output)
        else:
            with st.spinner("Step 1 — Outline…"):
                try:
                    chain = run_chain(task, config)
                    st.session_state[CHAIN_RESULT_KEY] = chain
                except Exception as exc:
                    st.error(f"Chain failed: {exc}")
                    return
            total_ms = chain.total_latency_ms
            total_tok = chain.total_tokens_out
            st.success(f"Chain complete — {total_ms:.0f} ms total · {total_tok} tokens out")

            for step in chain.steps:
                with st.expander(f"**{step.label}**", expanded=True):
                    st.markdown(step.output)
                    st.caption(f"{step.latency_ms:.0f} ms · {step.tokens_out} tokens out")
