"""UC3 — Analyse page: Image Intelligence (interactive Q&A)."""

import streamlit as st

from applications.media_projects.services.image_intelligence import ImageConfig, ask_about_image
from applications.media_projects.uc3.constants import (
    ANALYSIS_SESSION_KEY,
    CONFIG_SESSION_KEY,
    QA_HISTORY_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)

_SAMPLE_QUESTIONS = [
    "What is the main subject of this image?",
    "What text is visible in the image?",
    "Describe the mood or atmosphere of this image.",
    "What colours dominate this scene?",
]


def render() -> None:
    st.subheader("💬 Analyse — Visual Q&A")

    analysis = st.session_state.get(ANALYSIS_SESSION_KEY)
    if not analysis:
        st.warning("Process your image first (← Process tab).")
        return

    upload_data = st.session_state.get(UPLOAD_SESSION_KEY, {})
    config: ImageConfig = st.session_state.get(CONFIG_SESSION_KEY, ImageConfig())
    qa_history: list[dict] = st.session_state.get(QA_HISTORY_SESSION_KEY, [])

    # Context summary passed as system context
    context = f"Description: {analysis.description}\nExtracted text: {analysis.extracted_text}"

    # ── Sample questions ──────────────────────────────────────────────────
    if not qa_history:
        st.markdown("**Try a sample question:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_QUESTIONS):
            if cols[i % 2].button(q, key=f"media_uc3_sample_{i}", use_container_width=True):
                _ask(q, upload_data, config, context, qa_history)
                st.rerun()
        st.divider()

    # ── Q&A history ───────────────────────────────────────────────────────
    for turn in qa_history:
        with st.chat_message("user"):
            st.write(turn["q"])
        with st.chat_message("assistant"):
            st.write(turn["a"])

    # ── Chat input ────────────────────────────────────────────────────────
    question = st.chat_input("Ask anything about this image…")
    if question:
        _ask(question, upload_data, config, context, qa_history)
        st.rerun()

    if qa_history:
        if st.button("🗑 Clear Q&A history"):
            st.session_state[QA_HISTORY_SESSION_KEY] = []
            st.rerun()


def _ask(
    question: str,
    upload_data: dict,
    config: ImageConfig,
    context: str,
    qa_history: list[dict],
) -> None:
    with st.spinner("Thinking…"):
        try:
            answer = ask_about_image(
                question,
                upload_data["bytes"],
                upload_data.get("filename", "image.jpg"),
                config,
                context=context,
            )
        except Exception as exc:
            answer = f"Error: {exc}"
    qa_history.append({"q": question, "a": answer})
    st.session_state[QA_HISTORY_SESSION_KEY] = qa_history
