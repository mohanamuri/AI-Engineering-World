"""UC4 — Export page: Document Scanner."""

import json

import streamlit as st

from applications.media_projects.services.document_scanner import to_plain_text
from applications.media_projects.uc4.constants import SCAN_SESSION_KEY, UPLOAD_SESSION_KEY


def render() -> None:
    st.subheader("📥 Export")

    doc = st.session_state.get(SCAN_SESSION_KEY)
    if not doc:
        st.warning("Scan a document first.")
        return

    upload_data = st.session_state.get(UPLOAD_SESSION_KEY, {})
    stem = upload_data.get("filename", "document").rsplit(".", 1)[0]

    st.success("Scanned document ready to export.")

    doc_dict = {
        "source_file": upload_data.get("filename", ""),
        "timestamp": doc.timestamp,
        "document_type": doc.document_type,
        "title": doc.title,
        "sections": doc.sections,
        "all_text": doc.all_text,
        "metadata": doc.metadata,
    }

    col1, col2 = st.columns(2)
    col1.download_button(
        label="⬇️ Structured (JSON)",
        data=json.dumps(doc_dict, indent=2, ensure_ascii=False),
        file_name=f"{stem}_scan.json",
        mime="application/json",
        use_container_width=True,
    )
    col2.download_button(
        label="⬇️ Plain Text (TXT)",
        data=to_plain_text(doc),
        file_name=f"{stem}_scan.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.divider()
    st.markdown("#### Preview")
    tab1, tab2 = st.tabs(["Structured", "Raw JSON"])
    with tab1:
        st.markdown(f"**Type:** `{doc.document_type}`  |  **Title:** {doc.title}")
        for sec in doc.sections:
            heading = sec.get("heading", "")
            if heading:
                st.markdown(f"**{heading}**")
            st.write(sec.get("content", ""))
    with tab2:
        st.json(doc_dict)
