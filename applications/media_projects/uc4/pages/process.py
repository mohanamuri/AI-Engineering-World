"""UC4 — Process page: Document Scanner (Groq Vision extraction)."""

import streamlit as st

from applications.media_projects.services.document_scanner import ScannerConfig, scan_document
from applications.media_projects.uc4.constants import (
    CONFIG_SESSION_KEY,
    SCAN_SESSION_KEY,
    UPLOAD_SESSION_KEY,
)


def render() -> None:
    st.subheader("🔬 Scan")

    upload_data = st.session_state.get(UPLOAD_SESSION_KEY)
    if not upload_data:
        st.warning("Upload a document photo first (← Upload tab).")
        return

    config: ScannerConfig = st.session_state.get(CONFIG_SESSION_KEY, ScannerConfig())
    doc = st.session_state.get(SCAN_SESSION_KEY)

    col_img, col_info = st.columns([1, 1])
    with col_img:
        st.image(upload_data["bytes"], caption=upload_data["filename"], use_container_width=True)
    with col_info:
        st.caption(f"Model: `{config.vision_model}`")
        st.caption(f"Document type hint: `{config.document_type}`")
        st.caption(f"Temperature: `{config.temperature}`")

    if doc is None:
        st.info(
            "Click **Scan Document** to extract structured content from this image. "
            "Groq Vision will identify the document type, title, sections, and all text."
        )
        if st.button("🔬 Scan Document", type="primary", use_container_width=False):
            with st.spinner("Extracting document content with Groq Vision…"):
                try:
                    result = scan_document(
                        upload_data["bytes"], upload_data["filename"], config
                    )
                    st.session_state[SCAN_SESSION_KEY] = result
                    st.rerun()
                except Exception as exc:
                    st.error(f"Scan failed: {exc}")
    else:
        st.success("Document scanned successfully.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Type", doc.document_type)
        col2.metric("Sections", len(doc.sections))
        col3.metric("Words (est.)", doc.metadata.get("estimated_word_count", "—"))

        st.markdown(f"#### Title: {doc.title}")

        if doc.sections:
            st.markdown("#### Sections")
            for sec in doc.sections:
                heading = sec.get("heading", "")
                content = sec.get("content", "")
                if heading:
                    st.markdown(f"**{heading}**")
                st.write(content)
                st.divider()
        else:
            st.markdown("#### Extracted Text")
            st.text_area(
                "all_text",
                value=doc.all_text,
                height=300,
                label_visibility="collapsed",
                key="media_uc4_text_view",
            )

        with st.expander("Metadata", expanded=False):
            for k, v in doc.metadata.items():
                st.write(f"**{k}:** {v}")

        if st.button("🔄 Re-scan"):
            st.session_state.pop(SCAN_SESSION_KEY, None)
            st.rerun()

        st.info("Head to **Review** to validate → then **Export** to download →")
