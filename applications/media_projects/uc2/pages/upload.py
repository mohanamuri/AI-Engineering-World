"""UC2 — Upload page: Video Intelligence."""

from pathlib import Path

import streamlit as st

from applications.media_projects.services.video_intelligence import VideoConfig
from applications.media_projects.uc2.constants import (
    ANALYSIS_SESSION_KEY,
    CONFIG_SESSION_KEY,
    TRANSCRIPT_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)

_SAMPLE_PATH = Path(__file__).resolve().parents[4] / "data" / "media_docs" / "sample_meeting.mp4"

_LLM_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.3-70b-versatile",
    "gemma2-9b-it",
]


def render() -> None:
    st.subheader("📤 Upload")
    st.write("Upload a video recording. ffmpeg will extract the audio automatically.")

    # ── Sample loader ─────────────────────────────────────────────────────
    if _SAMPLE_PATH.exists():
        st.info(
            f"No video? Use the built-in sample — a short scripted meeting clip "
            f"({_SAMPLE_PATH.stat().st_size // 1024} KB)."
        )
        if st.button("📂 Load sample meeting video", type="primary", use_container_width=False):
            _confirm_upload(_SAMPLE_PATH.read_bytes(), _SAMPLE_PATH.name, None)
            st.rerun()
        st.divider()

    # ── File uploader ─────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Video file",
        type=["mp4", "mov", "avi", "mkv"],
        key="media_uc2_file_uploader",
        help="MP4 and MOV recommended. ffmpeg extracts audio before transcription.",
    )

    if uploaded:
        st.video(uploaded)
        st.caption(f"**{uploaded.name}** · {uploaded.size / 1024:.1f} KB")

        st.divider()
        st.markdown("#### Model settings")
        config: VideoConfig = st.session_state.get(CONFIG_SESSION_KEY, VideoConfig())
        col1, col2 = st.columns(2)
        with col1:
            llm_model = st.selectbox(
                "LLM model (analysis step)",
                _LLM_MODELS,
                index=_LLM_MODELS.index(config.llm_model) if config.llm_model in _LLM_MODELS else 0,
                key="media_uc2_llm_model",
            )
        with col2:
            temperature = st.slider(
                "Temperature",
                0.0, 1.0,
                value=config.temperature,
                step=0.05,
                key="media_uc2_temperature",
            )

        if st.button("✅ Confirm Upload", use_container_width=False):
            _confirm_upload(
                uploaded.getvalue(), uploaded.name,
                VideoConfig(llm_model=llm_model, temperature=temperature),
            )
            st.success(f"**{uploaded.name}** uploaded. Head to **Extract** to demux audio →")
    else:
        prior = st.session_state.get(UPLOAD_SESSION_KEY)
        if prior:
            st.info(f"Using: **{prior['filename']}** — upload a new file to replace.")

    with st.expander("How ffmpeg extraction works", expanded=False):
        st.markdown("""
ffmpeg runs server-side and extracts the audio track from the video:

```
ffmpeg -i input.mp4 -vn -acodec libmp3lame -ar 16000 -ac 1 output.mp3
```

| Flag | Effect |
|---|---|
| `-vn` | Drop the video stream |
| `-ar 16000` | 16 kHz sample rate (optimal for Whisper) |
| `-ac 1` | Mono channel |

The resulting MP3 is passed directly to Groq Whisper — no manual step needed.
        """)


def _confirm_upload(video_bytes: bytes, filename: str, config: VideoConfig | None) -> None:
    st.session_state[UPLOAD_SESSION_KEY] = {"bytes": video_bytes, "filename": filename}
    if config is not None:
        st.session_state[CONFIG_SESSION_KEY] = config
    elif CONFIG_SESSION_KEY not in st.session_state:
        st.session_state[CONFIG_SESSION_KEY] = VideoConfig()
    st.session_state.pop(TRANSCRIPT_SESSION_KEY, None)
    st.session_state.pop(ANALYSIS_SESSION_KEY, None)
