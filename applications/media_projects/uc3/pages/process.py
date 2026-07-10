"""UC3 — Process page: Image Intelligence (Groq Vision analysis)."""

import streamlit as st

from applications.media_projects.services.image_intelligence import (
    ImageConfig,
    analyse_image,
)
from applications.media_projects.uc3.constants import (
    ANALYSIS_SESSION_KEY,
    CONFIG_SESSION_KEY,
    QA_HISTORY_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)


def render() -> None:
    st.subheader("🔍 Process")

    upload_data = st.session_state.get(UPLOAD_SESSION_KEY)
    if not upload_data:
        st.warning("Upload an image first (← Upload tab).")
        return

    config: ImageConfig = st.session_state.get(CONFIG_SESSION_KEY, ImageConfig())
    analysis = st.session_state.get(ANALYSIS_SESSION_KEY)

    col_img, col_info = st.columns([1, 1])
    with col_img:
        st.image(upload_data["bytes"], caption=upload_data["filename"], use_container_width=True)
    with col_info:
        st.caption(f"Model: `{config.vision_model}`")
        st.caption(f"Temperature: `{config.temperature}`")

    if analysis is None:
        st.info(
            "Click **Analyse Image** to send this image to Groq Vision. "
            "The model will describe the scene, extract all text, identify objects, "
            "and detect dominant colours."
        )
        if st.button("👁️ Analyse Image", type="primary", use_container_width=False):
            with st.spinner("Sending to Groq Vision…"):
                try:
                    result = analyse_image(
                        upload_data["bytes"], upload_data["filename"], config
                    )
                    st.session_state[ANALYSIS_SESSION_KEY] = result
                    st.session_state.pop(QA_HISTORY_SESSION_KEY, None)
                    st.rerun()
                except Exception as exc:
                    st.error(f"Vision analysis failed: {exc}")
    else:
        st.success("Image analysis complete.")

        st.markdown("#### Description")
        st.write(analysis.description)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Extracted Text")
            st.info(analysis.extracted_text or "No text found")

            st.markdown("#### Detected Objects")
            if analysis.objects:
                for obj in analysis.objects:
                    st.markdown(f"- {obj}")
            else:
                st.caption("None detected.")

        with col2:
            st.markdown("#### Dominant Colours")
            if analysis.colours:
                for c in analysis.colours:
                    st.markdown(f"- {c}")
            else:
                st.caption("None detected.")

        if st.button("🔄 Re-analyse"):
            st.session_state.pop(ANALYSIS_SESSION_KEY, None)
            st.session_state.pop(QA_HISTORY_SESSION_KEY, None)
            st.rerun()

        st.info("Head to **Analyse** for interactive Q&A →")
