"""UC1 — Playground page: try zero-shot and few-shot interactively."""

import streamlit as st

from applications.prompt_projects.services.prompt_service import (
    PromptConfig,
    run_few_shot,
    run_zero_shot,
)
from applications.prompt_projects.uc1.constants import (
    CONFIG_SESSION_KEY,
    FEW_SHOT_RESULT_KEY,
    TASK_SESSION_KEY,
    ZERO_SHOT_RESULT_KEY,
)

_SAMPLE_TASKS = [
    "Write a one-sentence tagline for a productivity app called FocusFlow.",
    "Summarise this in one sentence: Remote work increases flexibility but can blur work-life boundaries.",
    "Classify the sentiment: 'The onboarding was smooth but support took 3 days to reply.'",
    "Rewrite this formally: 'Hey, just checking if you got my email?'",
]

_DEFAULT_EXAMPLES = [
    {"input": "Write a tagline for a fitness app called StrongMe.", "output": "StrongMe — built for the version of you that never quits."},
    {"input": "Write a tagline for a finance app called ClearCash.", "output": "ClearCash — every dollar, perfectly in focus."},
]


def render() -> None:
    st.subheader("🧪 Playground")
    st.write("Enter a task, choose a technique, and run it. Results are saved for the Compare page.")

    # ── Config ────────────────────────────────────────────────────────────────
    with st.expander("⚙️ Model settings", expanded=False):
        col1, col2 = st.columns(2)
        model = col1.selectbox("Model", ["gemma2-9b-it", "qwen/qwen3-32b", "moonshotai/kimi-k2-instruct"], index=0)
        temperature = col2.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        config = PromptConfig(model=model, temperature=temperature)
        st.session_state[CONFIG_SESSION_KEY] = config

    config: PromptConfig = st.session_state.get(CONFIG_SESSION_KEY, PromptConfig())

    # ── Task input ────────────────────────────────────────────────────────────
    st.markdown("#### Your task")
    st.caption("Pick a sample or write your own:")
    cols = st.columns(2)
    for i, sample in enumerate(_SAMPLE_TASKS):
        if cols[i % 2].button(sample, key=f"sample_uc1_{i}", use_container_width=True):
            st.session_state[TASK_SESSION_KEY] = sample

    task = st.text_area(
        "Task",
        value=st.session_state.get(TASK_SESSION_KEY, ""),
        height=80,
        placeholder="e.g. Write a tagline for a coffee brand called MorningBrew.",
        label_visibility="collapsed",
    )
    if task:
        st.session_state[TASK_SESSION_KEY] = task

    # ── Technique selector ────────────────────────────────────────────────────
    st.markdown("#### Technique")
    technique = st.radio(
        "Choose technique",
        ["Zero-shot", "Few-shot"],
        horizontal=True,
        label_visibility="collapsed",
        key="uc1_technique_radio",
    )

    if technique == "Few-shot":
        st.markdown("**Examples** (the model will follow this pattern):")
        for i, ex in enumerate(_DEFAULT_EXAMPLES):
            with st.expander(f"Example {i + 1}", expanded=True):
                ex["input"] = st.text_input(f"Input {i + 1}", ex["input"], key=f"ex_in_{i}")
                ex["output"] = st.text_input(f"Output {i + 1}", ex["output"], key=f"ex_out_{i}")

    # ── Run ───────────────────────────────────────────────────────────────────
    if st.button("▶ Run", type="primary", disabled=not task, use_container_width=True):
        with st.spinner(f"Running {technique}…"):
            try:
                if technique == "Zero-shot":
                    result = run_zero_shot(task, config)
                    st.session_state[ZERO_SHOT_RESULT_KEY] = result
                else:
                    result = run_few_shot(task, _DEFAULT_EXAMPLES, config)
                    st.session_state[FEW_SHOT_RESULT_KEY] = result
            except Exception as exc:
                st.error(f"Groq call failed: {exc}")
                return

        st.success(f"Done — {result.latency_ms:.0f} ms · {result.tokens_out} tokens out")
        st.markdown(f"**Output ({technique}):**")
        st.markdown(result.output)

        with st.expander("View full prompt sent to model", expanded=False):
            st.code(result.prompt_used, language="text")
