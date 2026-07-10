"""UC3 — Playground page: try structured output."""

import json

import streamlit as st

from applications.prompt_projects.services.prompt_service import (
    DEFAULT_SCHEMA,
    PromptConfig,
    run_freeform,
    run_structured,
)
from applications.prompt_projects.uc3.constants import (
    CONFIG_SESSION_KEY,
    FREEFORM_RESULT_KEY,
    SCHEMA_SESSION_KEY,
    STRUCTURED_RESULT_KEY,
    TASK_SESSION_KEY,
)

_SAMPLE_TASKS = [
    "Analyse this review: 'The laptop runs hot under load but the display is stunning.'",
    "Summarise this feedback: 'Delivery was fast but packaging was damaged on arrival.'",
    "Extract insights from: 'The team is motivated but lacks clear direction from management.'",
    "Analyse: 'Great price point but the app crashes frequently on Android.'",
]


def render() -> None:
    st.subheader("🧪 Playground")
    st.write("Run the same task as freeform or structured JSON output, and see the difference.")

    with st.expander("⚙️ Model settings", expanded=False):
        col1, col2 = st.columns(2)
        model = col1.selectbox("Model", ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"], index=0, key="uc3_model")
        temperature = col2.slider("Temperature", 0.0, 1.0, 0.1, 0.1, key="uc3_temp",
                                   help="Low temperature = more consistent JSON output")
        config = PromptConfig(model=model, temperature=temperature)
        st.session_state[CONFIG_SESSION_KEY] = config

    config: PromptConfig = st.session_state.get(CONFIG_SESSION_KEY, PromptConfig(temperature=0.1))

    st.markdown("#### Task")
    cols = st.columns(2)
    for i, s in enumerate(_SAMPLE_TASKS):
        if cols[i % 2].button(s, key=f"sample_uc3_{i}", use_container_width=True):
            st.session_state[TASK_SESSION_KEY] = s

    task = st.text_area(
        "Task",
        value=st.session_state.get(TASK_SESSION_KEY, ""),
        height=80,
        placeholder="e.g. Analyse this review: 'Great product but terrible support.'",
        label_visibility="collapsed",
    )
    if task:
        st.session_state[TASK_SESSION_KEY] = task

    st.markdown("#### Output schema (JSON)")
    schema_str = st.text_area(
        "Schema",
        value=json.dumps(
            st.session_state.get(SCHEMA_SESSION_KEY, DEFAULT_SCHEMA),
            indent=2,
        ),
        height=180,
        help="Define exactly what fields the model should return.",
    )
    try:
        schema = json.loads(schema_str)
        st.session_state[SCHEMA_SESSION_KEY] = schema
    except json.JSONDecodeError:
        st.warning("Schema is not valid JSON — using default.")
        schema = DEFAULT_SCHEMA

    technique = st.radio(
        "Technique",
        ["Freeform", "Structured JSON"],
        horizontal=True,
        label_visibility="collapsed",
        key="uc3_technique_radio",
    )

    if st.button("▶ Run", type="primary", disabled=not task, use_container_width=True):
        with st.spinner(f"Running {technique}…"):
            try:
                if technique == "Freeform":
                    result = run_freeform(task, config)
                    st.session_state[FREEFORM_RESULT_KEY] = result
                else:
                    result = run_structured(task, schema, config)
                    st.session_state[STRUCTURED_RESULT_KEY] = result
            except Exception as exc:
                st.error(f"Groq call failed: {exc}")
                return

        st.success(f"Done — {result.latency_ms:.0f} ms · {result.tokens_out} tokens out")

        if technique == "Structured JSON":
            st.markdown("**Parsed JSON output:**")
            try:
                parsed = json.loads(result.output)
                st.json(parsed)
            except json.JSONDecodeError:
                st.warning("Output is not valid JSON — showing raw:")
                st.code(result.output, language="text")
        else:
            st.markdown("**Freeform output:**")
            st.markdown(result.output)

        with st.expander("View full prompt sent to model", expanded=False):
            st.code(result.prompt_used, language="text")
