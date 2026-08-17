"""Media Projects — UC4: Document Scanner entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.media_projects.uc4.constants import NAVIGATION_SESSION_KEY
from applications.media_projects.uc4.pages import analyse, concept, export, process, upload


PAGES = {
    "📖 Concept":    concept.render,
    "📤 Upload":      upload.render,
    "🔬 Scan":        process.render,
    "📋 Review":      analyse.render,
    "📥 Export":      export.render,
}


def run() -> None:
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("← Home", use_container_width=True):
            go_home()
            st.rerun()

    st.markdown(
        """
        <section class="aiew-tier-banner aiew-tb--t4">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC4</div>
                <div>
                    <div class="aiew-tb-cap">Media Projects · Use Case 4 of 4</div>
                    <div class="aiew-tb-title">Document Scanner</div>
                    <div class="aiew-tb-desc">
                        Upload a photo of any document, whiteboard, or slide.
                        Groq Vision extracts the full structured content —
                        title, sections, all text — and lets you export it as
                        clean JSON or plain text.
                    </div>
                    <div class="aiew-tb-flow">📄 Photo → 👁️ Groq Vision → 🗂️ Structured Extract → 📥 JSON / TXT</div>
                    <div>
                        <span class="aiew-tech-pill">Groq Vision</span>
                        <span class="aiew-tech-pill">llama-4-scout-17b</span>
                        <span class="aiew-tech-pill">Document Digitisation</span>
                        <span class="aiew-tech-pill">Structured Export</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("About this use case", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### What this use case does")
            st.write(
                "Upload a photo of any document, whiteboard, meeting notes, "
                "or presentation slide. "
                "Groq Vision reads the image and returns structured JSON: "
                "document type, title, sections with headings, all verbatim text, "
                "and metadata (language, tables, diagrams). "
                "Export as JSON or clean plain text."
            )
            st.markdown("#### New concept introduced")
            st.info(
                "**UC4** completes the media pipeline: vision → structured data. "
                "A photo of any document becomes machine-readable in one API call — "
                "the foundation for automated document digitisation workflows."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Vision model", "Output", "Export formats"],
                "Technology": [
                    "qwen/qwen3-32b",
                    "Structured JSON (type, title, sections, metadata)",
                    "JSON + plain text download",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Document Scanner · UC4 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Scan → Review → Export")
        st.divider()
        st.caption("👁️ Vision  ·  🗂️ Structure  ·  📥 JSON / TXT")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
