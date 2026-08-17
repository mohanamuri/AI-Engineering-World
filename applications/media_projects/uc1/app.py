"""Media Projects — UC1: Meeting Intelligence entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.media_projects.uc1.constants import NAVIGATION_SESSION_KEY
from applications.media_projects.uc1.pages import analyse, concept, export, process, upload


PAGES = {
    "📖 Concept":    concept.render,
    "📤 Upload":      upload.render,
    "🎙️ Transcribe":  process.render,
    "🧠 Analyse":     analyse.render,
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
        <section class="aiew-tier-banner aiew-tb--t1">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC1</div>
                <div>
                    <div class="aiew-tb-cap">Media Projects · Use Case 1 of 4</div>
                    <div class="aiew-tb-title">Meeting Intelligence</div>
                    <div class="aiew-tb-desc">
                        Upload any audio recording and get a complete meeting report:
                        transcript, summary, decisions, action items, and sentiment —
                        all powered by Groq Whisper and a Groq LLM.
                    </div>
                    <div class="aiew-tb-flow">🎙️ Upload → 📝 Transcribe → 🧠 Analyse → 📥 Export</div>
                    <div>
                        <span class="aiew-tech-pill">Groq Whisper</span>
                        <span class="aiew-tech-pill">Groq LLM</span>
                        <span class="aiew-tech-pill">Speech-to-Text</span>
                        <span class="aiew-tech-pill">Structured Extraction</span>
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
                "Upload any audio recording (.mp3, .wav, .m4a). "
                "Groq Whisper transcribes it to text. "
                "An LLM then reads the transcript and extracts a structured report: "
                "summary, decisions made, action items with owners, overall sentiment, "
                "and key topics discussed."
            )
            st.markdown("#### New concept introduced")
            st.info(
                "**UC1** introduces speech-to-text + LLM structured extraction: "
                "one audio file → one complete machine-readable meeting report. "
                "No manual note-taking required."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Transcription", "LLM", "Output format"],
                "Technology": [
                    "Groq Whisper (whisper-large-v3)",
                    "Groq LLaMA (llama-3.3-70b-versatile)",
                    "JSON report + plain text",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Meeting Intelligence · UC1 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Transcribe → Analyse → Export")
        st.divider()
        st.caption("🎙️ Whisper  ·  🧠 LLM extraction  ·  📥 JSON / TXT")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
