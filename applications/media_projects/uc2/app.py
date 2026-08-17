"""Media Projects — UC2: Video Intelligence entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.media_projects.uc2.constants import NAVIGATION_SESSION_KEY
from applications.media_projects.uc2.pages import analyse, concept, export, process, upload


PAGES = {
    "📖 Concept":    concept.render,
    "📤 Upload":      upload.render,
    "🎬 Extract":     process.render,
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
        <section class="aiew-tier-banner aiew-tb--t2">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC2</div>
                <div>
                    <div class="aiew-tb-cap">Media Projects · Use Case 2 of 4</div>
                    <div class="aiew-tb-title">Video Intelligence</div>
                    <div class="aiew-tb-desc">
                        Upload a video recording. ffmpeg strips the audio track,
                        Groq Whisper transcribes it, and an LLM produces the same
                        structured meeting report as UC1 — no manual audio extraction needed.
                    </div>
                    <div class="aiew-tb-flow">🎬 Video → 🔊 ffmpeg → 🎙️ Whisper → 🧠 Analyse → 📥 Export</div>
                    <div>
                        <span class="aiew-tech-pill">ffmpeg</span>
                        <span class="aiew-tech-pill">Groq Whisper</span>
                        <span class="aiew-tech-pill">Groq LLM</span>
                        <span class="aiew-tech-pill">Video-to-Text</span>
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
                "Upload any video file (.mp4, .mov). "
                "ffmpeg extracts the audio track (16 kHz mono MP3). "
                "Groq Whisper transcribes it. "
                "An LLM then produces the same structured meeting report as UC1."
            )
            st.markdown("#### New concept introduced")
            st.info(
                "**UC2** adds a video demux step before the UC1 pipeline: "
                "ffmpeg removes the need to manually extract audio. "
                "The Whisper + LLM pipeline is identical to Meeting Intelligence."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Audio extraction", "Transcription", "LLM"],
                "Technology": [
                    "ffmpeg (system, 16 kHz mono)",
                    "Groq Whisper (whisper-large-v3)",
                    "Groq LLaMA (mixtral-8x7b-32768)",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Video Intelligence · UC2 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Extract → Analyse → Export")
        st.divider()
        st.caption("🎬 ffmpeg  ·  🎙️ Whisper  ·  🧠 LLM  ·  📥 Export")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
