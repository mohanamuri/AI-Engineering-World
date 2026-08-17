"""UC3 — Upload page: Image Intelligence."""

from pathlib import Path

import streamlit as st

from applications.media_projects.services.image_intelligence import ImageConfig
from applications.media_projects.uc3.constants import (
    ANALYSIS_SESSION_KEY,
    CONFIG_SESSION_KEY,
    QA_HISTORY_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)

_SAMPLE_PATH = Path(__file__).resolve().parents[4] / "data" / "media_docs" / "sample_image.png"

_VISION_MODELS = [
    "compound-beta-mini",
    "llama-3.2-11b-vision-preview",
]


def render() -> None:
    st.subheader("📤 Upload")
    st.write("Upload any image to describe, extract text, and ask questions about it.")

    # ── Sample loader ─────────────────────────────────────────────────────
    if _SAMPLE_PATH.exists():
        st.info(
            f"No image? Use the built-in sample — a generated scene with embedded text "
            f"({_SAMPLE_PATH.stat().st_size // 1024} KB)."
        )
        if st.button("📂 Load sample image", type="primary", use_container_width=False):
            _confirm_upload(_SAMPLE_PATH.read_bytes(), _SAMPLE_PATH.name, None)
            st.rerun()
        st.divider()

    # ── File uploader ─────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Image file",
        type=["jpg", "jpeg", "png", "webp"],
        key="media_uc3_file_uploader",
        help="JPG, PNG, WebP supported",
    )

    if uploaded:
        st.image(uploaded, caption=uploaded.name, use_container_width=True)
        st.caption(f"**{uploaded.name}** · {uploaded.size / 1024:.1f} KB")

        st.divider()
        st.markdown("#### Model settings")
        config: ImageConfig = st.session_state.get(CONFIG_SESSION_KEY, ImageConfig())
        col1, col2 = st.columns(2)
        with col1:
            vision_model = st.selectbox(
                "Vision model",
                _VISION_MODELS,
                index=_VISION_MODELS.index(config.vision_model) if config.vision_model in _VISION_MODELS else 0,
                key="media_uc3_vision_model",
            )
        with col2:
            temperature = st.slider(
                "Temperature",
                0.0, 1.0,
                value=config.temperature,
                step=0.05,
                key="media_uc3_temperature",
            )

        if st.button("✅ Confirm Upload", use_container_width=False):
            _confirm_upload(
                uploaded.getvalue(), uploaded.name,
                ImageConfig(vision_model=vision_model, temperature=temperature),
            )
            st.success(f"**{uploaded.name}** uploaded. Head to **Process** to analyse →")
    else:
        prior = st.session_state.get(UPLOAD_SESSION_KEY)
        if prior:
            st.info(f"Using: **{prior['filename']}** — upload a new file to replace.")


def _confirm_upload(image_bytes: bytes, filename: str, config: ImageConfig | None) -> None:
    st.session_state[UPLOAD_SESSION_KEY] = {"bytes": image_bytes, "filename": filename}
    if config is not None:
        st.session_state[CONFIG_SESSION_KEY] = config
    elif CONFIG_SESSION_KEY not in st.session_state:
        st.session_state[CONFIG_SESSION_KEY] = ImageConfig()
    st.session_state.pop(ANALYSIS_SESSION_KEY, None)
    st.session_state.pop(QA_HISTORY_SESSION_KEY, None)
