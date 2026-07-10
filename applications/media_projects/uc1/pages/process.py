"""UC1 — Process page: Meeting Intelligence (Groq Whisper transcription)."""

import streamlit as st

from applications.media_projects.services.meeting_intelligence import (
    MeetingConfig,
    transcribe_audio,
)
from applications.media_projects.uc1.constants import (
    ANALYSIS_SESSION_KEY,
    CONFIG_SESSION_KEY,
    TRANSCRIPT_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)


def render() -> None:
    st.subheader("🎙️ Transcribe")

    upload_data = st.session_state.get(UPLOAD_SESSION_KEY)
    if not upload_data:
        st.warning("Upload an audio file first (← Upload tab).")
        return

    config: MeetingConfig = st.session_state.get(CONFIG_SESSION_KEY, MeetingConfig())
    result = st.session_state.get(TRANSCRIPT_SESSION_KEY)

    st.caption(f"File: **{upload_data['filename']}** · Model: `{config.whisper_model}`")

    if result is None:
        st.info("Click **Transcribe** to send your audio to Groq Whisper.")
        if st.button("🎙️ Transcribe Audio", type="primary", use_container_width=False):
            with st.spinner("Transcribing with Groq Whisper…"):
                try:
                    r = transcribe_audio(upload_data["bytes"], upload_data["filename"], config)
                    st.session_state[TRANSCRIPT_SESSION_KEY] = r
                    st.session_state.pop(ANALYSIS_SESSION_KEY, None)
                    st.rerun()
                except Exception as exc:
                    st.error(f"Transcription failed: {exc}")
    else:
        st.success("Transcription complete.")

        col1, col2 = st.columns(2)
        col1.metric("Duration", f"{result.duration:.1f} s" if result.duration else "—")
        col2.metric("Word count", len(result.text.split()))

        st.markdown("#### Transcript")
        st.text_area(
            "transcript",
            value=result.text,
            height=300,
            label_visibility="collapsed",
            key="media_uc1_transcript_view",
        )

        col_re, col_next = st.columns([1, 3])
        with col_re:
            if st.button("🔄 Re-transcribe"):
                st.session_state.pop(TRANSCRIPT_SESSION_KEY, None)
                st.session_state.pop(ANALYSIS_SESSION_KEY, None)
                st.rerun()

        st.info("Head to **Analyse** to extract meeting insights →")
