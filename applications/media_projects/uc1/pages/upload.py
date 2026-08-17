"""UC1 — Upload page: Meeting Intelligence."""

from pathlib import Path

import streamlit as st

from applications.media_projects.services.meeting_intelligence import MeetingConfig
from applications.media_projects.uc1.constants import (
    ANALYSIS_SESSION_KEY,
    CONFIG_SESSION_KEY,
    TRANSCRIPT_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)

_SAMPLE_PATH = Path(__file__).resolve().parents[4] / "data" / "media_docs" / "sample_meeting.wav"

_LLM_MODELS = [
    "gemma2-9b-it",
    "gemma2-9b-it",
    "gemma2-9b-it",
]


def render() -> None:
    st.subheader("📤 Upload")
    st.write("Upload an audio recording from a meeting or conversation.")

    # ── Sample loader (same pattern as ML/DL projects) ────────────────────
    if _SAMPLE_PATH.exists():
        st.info(
            f"No audio file? Use the built-in sample — a short scripted meeting recording "
            f"({_SAMPLE_PATH.stat().st_size // 1024} KB)."
        )
        if st.button("📂 Load sample meeting audio", type="primary", use_container_width=False):
            _confirm_upload(_SAMPLE_PATH.read_bytes(), _SAMPLE_PATH.name, None)
            st.rerun()
        st.divider()

    # ── File uploader ─────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Audio file",
        type=["mp3", "wav", "m4a", "ogg", "flac"],
        key="media_uc1_file_uploader",
        help="Supports MP3, WAV, M4A, OGG, FLAC — up to ~25 MB on Groq free tier",
    )

    if uploaded:
        st.audio(uploaded)
        st.caption(f"**{uploaded.name}** · {uploaded.size / 1024:.1f} KB")

        st.divider()
        st.markdown("#### Model settings")
        config: MeetingConfig = st.session_state.get(CONFIG_SESSION_KEY, MeetingConfig())
        col1, col2 = st.columns(2)
        with col1:
            llm_model = st.selectbox(
                "LLM model (analysis step)",
                _LLM_MODELS,
                index=_LLM_MODELS.index(config.llm_model) if config.llm_model in _LLM_MODELS else 0,
                key="media_uc1_llm_model",
            )
        with col2:
            temperature = st.slider(
                "Temperature",
                0.0, 1.0,
                value=config.temperature,
                step=0.05,
                key="media_uc1_temperature",
            )

        if st.button("✅ Confirm Upload", use_container_width=False):
            _confirm_upload(
                uploaded.getvalue(), uploaded.name,
                MeetingConfig(llm_model=llm_model, temperature=temperature),
            )
            st.success(f"**{uploaded.name}** uploaded. Head to **Transcribe** →")
    else:
        prior = st.session_state.get(UPLOAD_SESSION_KEY)
        if prior:
            st.info(f"Using: **{prior['filename']}** — upload a new file to replace.")

    with st.expander("Format guide & tips", expanded=False):
        st.markdown("""
| Format | Notes |
|---|---|
| **MP3** | Most common; variable bitrate is fine |
| **WAV** | Lossless, larger files |
| **M4A** | iOS / macOS recordings |
| **OGG / FLAC** | Open formats |

**Tips for best results:** clear speech, minimal background noise, files under 25 MB.
        """)


def _confirm_upload(audio_bytes: bytes, filename: str, config: MeetingConfig | None) -> None:
    st.session_state[UPLOAD_SESSION_KEY] = {"bytes": audio_bytes, "filename": filename}
    if config is not None:
        st.session_state[CONFIG_SESSION_KEY] = config
    elif CONFIG_SESSION_KEY not in st.session_state:
        st.session_state[CONFIG_SESSION_KEY] = MeetingConfig()
    # Clear downstream results
    st.session_state.pop(TRANSCRIPT_SESSION_KEY, None)
    st.session_state.pop(ANALYSIS_SESSION_KEY, None)
