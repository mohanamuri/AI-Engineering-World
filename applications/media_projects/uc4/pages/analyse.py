"""UC4 — Review page: Document Scanner (validate extracted content)."""

import streamlit as st

from applications.media_projects.uc4.constants import SCAN_SESSION_KEY, UPLOAD_SESSION_KEY


def render() -> None:
    st.subheader("📋 Review")

    doc = st.session_state.get(SCAN_SESSION_KEY)
    if not doc:
        st.warning("Scan a document first (← Scan tab).")
        return

    upload_data = st.session_state.get(UPLOAD_SESSION_KEY, {})

    st.success("Document extracted. Review the structured output below before exporting.")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(upload_data.get("bytes", b""), caption="Source document", use_container_width=True)

    with col2:
        st.markdown(f"**Document type:** `{doc.document_type}`")
        st.markdown(f"**Title:** {doc.title}")
        st.markdown(f"**Sections:** {len(doc.sections)}")

        if doc.metadata:
            md = doc.metadata
            flags = []
            if md.get("has_tables"):
                flags.append("📊 Tables detected")
            if md.get("has_diagrams"):
                flags.append("📐 Diagrams detected")
            if md.get("language"):
                flags.append(f"🌐 Language: {md['language']}")
            if flags:
                st.markdown(" · ".join(flags))

    st.divider()

    if doc.sections:
        st.markdown("#### Extracted Sections")
        for i, sec in enumerate(doc.sections):
            heading = sec.get("heading", f"Section {i + 1}")
            content = sec.get("content", "")
            with st.expander(heading or f"Section {i + 1}", expanded=(i == 0)):
                st.write(content)
    else:
        st.markdown("#### All Extracted Text")
        st.text_area(
            "raw_text",
            value=doc.all_text,
            height=400,
            label_visibility="collapsed",
            key="media_uc4_review_text",
        )

    st.info("Head to **Export** to download as JSON or plain text →")
