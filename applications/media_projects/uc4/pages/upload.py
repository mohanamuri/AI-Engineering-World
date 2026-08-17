"""UC4 — Upload page: Document Scanner."""

from pathlib import Path

import streamlit as st

from applications.media_projects.services.document_scanner import ScannerConfig
from applications.media_projects.uc4.constants import (
    CONFIG_SESSION_KEY,
    SCAN_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)

_SAMPLE_PATH = Path(__file__).resolve().parents[4] / "data" / "media_docs" / "sample_document.png"

_VISION_MODELS = [
    "gemma2-9b-it",
    "llama-3.2-11b-vision-preview",
]

_DOC_TYPES = ["auto", "meeting_notes", "whiteboard", "slide", "form", "report"]


def render() -> None:
    st.subheader("📤 Upload")
    st.write(
        "Upload a photo of any document, whiteboard, or slide. "
        "Groq Vision will extract the full structured content."
    )

    # ── Sample loader ─────────────────────────────────────────────────────
    if _SAMPLE_PATH.exists():
        st.info(
            f"No document photo? Use the built-in sample — a meeting notes image "
            f"({_SAMPLE_PATH.stat().st_size // 1024} KB)."
        )
        if st.button("📂 Load sample document", type="primary", use_container_width=False):
            _confirm_upload(_SAMPLE_PATH.read_bytes(), _SAMPLE_PATH.name, None)
            st.rerun()
        st.divider()

    # ── File uploader ─────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Document photo",
        type=["jpg", "jpeg", "png", "webp"],
        key="media_uc4_file_uploader",
        help="JPG, PNG, or WebP photo of any document",
    )

    if uploaded:
        st.image(uploaded, caption=uploaded.name, use_container_width=True)
        st.caption(f"**{uploaded.name}** · {uploaded.size / 1024:.1f} KB")

        st.divider()
        st.markdown("#### Scanner settings")
        config: ScannerConfig = st.session_state.get(CONFIG_SESSION_KEY, ScannerConfig())
        col1, col2, col3 = st.columns(3)
        with col1:
            vision_model = st.selectbox(
                "Vision model",
                _VISION_MODELS,
                index=_VISION_MODELS.index(config.vision_model) if config.vision_model in _VISION_MODELS else 0,
                key="media_uc4_vision_model",
            )
        with col2:
            document_type = st.selectbox(
                "Document type hint",
                _DOC_TYPES,
                index=_DOC_TYPES.index(config.document_type) if config.document_type in _DOC_TYPES else 0,
                key="media_uc4_doc_type",
                help="'auto' lets the model decide; a hint improves accuracy",
            )
        with col3:
            temperature = st.slider(
                "Temperature",
                0.0, 0.5,
                value=config.temperature,
                step=0.05,
                key="media_uc4_temperature",
                help="Keep low (0.0) for accurate extraction",
            )

        if st.button("✅ Confirm Upload", use_container_width=False):
            _confirm_upload(
                uploaded.getvalue(), uploaded.name,
                ScannerConfig(
                    vision_model=vision_model,
                    document_type=document_type,
                    temperature=temperature,
                ),
            )
            st.success(f"**{uploaded.name}** uploaded. Head to **Scan** to extract content →")
    else:
        prior = st.session_state.get(UPLOAD_SESSION_KEY)
        if prior:
            st.info(f"Using: **{prior['filename']}** — upload a new file to replace.")

    with st.expander("What makes a good document photo?", expanded=False):
        st.markdown("""
- **Flat, parallel shot** — avoid angled photos (keystone distortion confuses the model)
- **Good lighting** — no harsh shadows across the text
- **Readable font size** — text should be legible to the human eye
- **Works with:** printed documents, handwritten notes, whiteboards, presentation slides, forms
        """)


def _confirm_upload(image_bytes: bytes, filename: str, config: ScannerConfig | None) -> None:
    st.session_state[UPLOAD_SESSION_KEY] = {"bytes": image_bytes, "filename": filename}
    if config is not None:
        st.session_state[CONFIG_SESSION_KEY] = config
    elif CONFIG_SESSION_KEY not in st.session_state:
        st.session_state[CONFIG_SESSION_KEY] = ScannerConfig()
    st.session_state.pop(SCAN_SESSION_KEY, None)
