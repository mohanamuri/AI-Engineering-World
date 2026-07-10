"""Media Projects — UC3: Image Intelligence entry point."""

import streamlit as st
from core.launcher import go_home

from applications.media_projects.uc3.constants import NAVIGATION_SESSION_KEY
from applications.media_projects.uc3.pages import analyse, export, process, upload


PAGES = {
    "📤 Upload":      upload.render,
    "🔍 Process":     process.render,
    "💬 Analyse":     analyse.render,
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
        <section class="aiew-tier-banner aiew-tb--t3">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC3</div>
                <div>
                    <div class="aiew-tb-cap">Media Projects · Use Case 3 of 4</div>
                    <div class="aiew-tb-title">Image Intelligence</div>
                    <div class="aiew-tb-desc">
                        Upload any image and let Groq Vision describe the scene,
                        extract all embedded text, identify objects, and answer
                        your follow-up questions — no OCR step required.
                    </div>
                    <div class="aiew-tb-flow">🖼️ Image → 👁️ Groq Vision → 📝 Description + Text → 💬 Q&amp;A</div>
                    <div>
                        <span class="aiew-tech-pill">Groq Vision</span>
                        <span class="aiew-tech-pill">llama-4-scout-17b</span>
                        <span class="aiew-tech-pill">Visual Q&amp;A</span>
                        <span class="aiew-tech-pill">OCR-free extraction</span>
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
                "Upload any image (.jpg, .png). "
                "Groq Vision processes the raw pixels — no separate OCR tool needed. "
                "It describes the scene, extracts all text it can see, lists objects, "
                "and identifies dominant colours. "
                "Then ask follow-up questions about the image interactively."
            )
            st.markdown("#### New concept introduced")
            st.info(
                "**UC3** introduces vision-language models: "
                "the model 'sees' and 'reads' an image in a single inference call. "
                "No traditional OCR pipeline — pixel → text happens end-to-end."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Vision model", "Framework", "Output"],
                "Technology": [
                    "meta-llama/llama-4-scout-17b-16e-instruct",
                    "LangChain + Groq",
                    "Structured JSON + interactive Q&A",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Image Intelligence · UC3 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Process → Q&A → Export")
        st.divider()
        st.caption("👁️ Vision  ·  📝 Describe + OCR  ·  💬 Q&A")

    PAGES[page]()
