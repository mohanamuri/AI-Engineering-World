"""UC2 — Process page: Video Intelligence (ffmpeg + Groq Whisper)."""

import streamlit as st

from applications.media_projects.services.video_intelligence import VideoConfig, process_video
from applications.media_projects.uc2.constants import (
    ANALYSIS_SESSION_KEY,
    CONFIG_SESSION_KEY,
    TRANSCRIPT_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)


def render() -> None:
    st.subheader("🎬 Extract & Transcribe")

    upload_data = st.session_state.get(UPLOAD_SESSION_KEY)
    if not upload_data:
        st.warning("Upload a video file first (← Upload tab).")
        return

    config: VideoConfig = st.session_state.get(CONFIG_SESSION_KEY, VideoConfig())
    result = st.session_state.get(TRANSCRIPT_SESSION_KEY)

    st.caption(f"File: **{upload_data['filename']}**")

    if result is None:
        st.info(
            "Click **Extract & Transcribe** to: \n"
            "1. Strip the audio with ffmpeg (16 kHz mono MP3)\n"
            "2. Send it to Groq Whisper for transcription"
        )
        if st.button("🎬 Extract & Transcribe", type="primary", use_container_width=False):
            with st.spinner("Running ffmpeg + Groq Whisper…"):
                try:
                    r = process_video(
                        upload_data["bytes"], upload_data["filename"], config
                    )
                    st.session_state[TRANSCRIPT_SESSION_KEY] = r
                    st.session_state.pop(ANALYSIS_SESSION_KEY, None)
                    st.rerun()
                except FileNotFoundError:
                    st.error(
                        "ffmpeg not found. Install it with: "
                        "`sudo apt-get install ffmpeg` (Linux) or `brew install ffmpeg` (macOS)."
                    )
                except Exception as exc:
                    st.error(f"Processing failed: {exc}")
    else:
        st.success("Audio extracted and transcribed.")

        col1, col2 = st.columns(2)
        col1.metric("Duration", f"{result.duration:.1f} s" if result.duration else "—")
        col2.metric("Word count", len(result.text.split()))

        st.markdown("#### Transcript")
        st.text_area(
            "transcript",
            value=result.text,
            height=300,
            label_visibility="collapsed",
            key="media_uc2_transcript_view",
        )

        if st.button("🔄 Re-process"):
            st.session_state.pop(TRANSCRIPT_SESSION_KEY, None)
            st.session_state.pop(ANALYSIS_SESSION_KEY, None)
            st.rerun()

        st.info("Head to **Analyse** to extract meeting insights →")
