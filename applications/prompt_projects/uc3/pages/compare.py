"""UC3 — Compare page: freeform vs structured JSON side by side."""

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


def render() -> None:
    st.subheader("⚖️ Freeform vs Structured JSON")
    st.write("Run both on the same task — see parseable JSON on the right vs unstructured prose on the left.")

    config: PromptConfig = st.session_state.get(CONFIG_SESSION_KEY, PromptConfig(temperature=0.1))
    schema = st.session_state.get(SCHEMA_SESSION_KEY, DEFAULT_SCHEMA)
    saved_task = st.session_state.get(TASK_SESSION_KEY, "")

    task = st.text_area(
        "Task",
        value=saved_task,
        height=80,
        placeholder="e.g. Analyse this review: 'Great product but terrible support.'",
    )

    if st.button("⚖️ Run Both", type="primary", disabled=not task, use_container_width=True):
        st.session_state[TASK_SESSION_KEY] = task
        col1, col2 = st.columns(2)
        with col1:
            with st.spinner("Running Freeform…"):
                try:
                    fr = run_freeform(task, config)
                    st.session_state[FREEFORM_RESULT_KEY] = fr
                except Exception as exc:
                    st.error(f"Freeform failed: {exc}")
                    return
        with col2:
            with st.spinner("Running Structured…"):
                try:
                    sr = run_structured(task, schema, config)
                    st.session_state[STRUCTURED_RESULT_KEY] = sr
                except Exception as exc:
                    st.error(f"Structured failed: {exc}")
                    return

    fr = st.session_state.get(FREEFORM_RESULT_KEY)
    sr = st.session_state.get(STRUCTURED_RESULT_KEY)

    if not fr and not sr:
        st.info("Enter a task and click **Run Both** to compare.")
        return

    st.divider()
    col_f, col_s = st.columns(2)

    with col_f:
        st.markdown("### 📝 Freeform")
        if fr:
            c1, c2 = st.columns(2)
            c1.metric("Latency", f"{fr.latency_ms:.0f} ms")
            c2.metric("Tokens out", fr.tokens_out)
            with st.container(border=True):
                st.markdown(fr.output)
            st.caption("⚠️ Try `json.loads()` on this — it will fail.")

    with col_s:
        st.markdown("### 🗂️ Structured JSON")
        if sr:
            c1, c2 = st.columns(2)
            c1.metric("Latency", f"{sr.latency_ms:.0f} ms")
            c2.metric("Tokens out", sr.tokens_out)
            try:
                parsed = json.loads(sr.output)
                st.json(parsed)
                st.caption("✅ `json.loads()` works every time.")
            except json.JSONDecodeError:
                st.warning("Not valid JSON this run — lower temperature helps.")
                st.code(sr.output, language="text")
