"""Loan Eligibility — RAG (T4) application entry point."""

import streamlit as st
from core.launcher import go_home

from applications.loan_rag.constants import (
    NAVIGATION_SESSION_KEY,
    UPLOAD_PAGE_LABEL,
)
from applications.loan_rag.pages import (
    chat,
    configure,
    download,
    explore,
    history,
    upload,
)


PAGES = {
    UPLOAD_PAGE_LABEL: upload.render,
    "🔍 Explore Chunks": explore.render,
    "⚙️ Configure RAG": configure.render,
    "💬 Chat": chat.render,
    "📜 History": history.render,
    "⬇ Download": download.render,
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
                <div class="aiew-tier-badge-lg">T4</div>
                <div>
                    <div class="aiew-tb-cap">Retrieval-Augmented Generation · Tier 4 of 6</div>
                    <div class="aiew-tb-title">Loan Policy Q&amp;A</div>
                    <div class="aiew-tb-desc">
                        RAG pipeline — load a loan policy PDF, chunk and embed it into ChromaDB,
                        then answer natural-language questions grounded in the actual document.
                        No hallucination: every answer cites its source chunk.
                    </div>
                    <div class="aiew-tb-flow">📄 Load → 🔍 Chunk → 🧮 Embed → 💬 Chat → 📜 History → ⬇ Export</div>
                    <div>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">HuggingFace</span>
                        <span class="aiew-tech-pill">llama-3.1-8b</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<div class="aiew-side-label">Loan RAG · T4 workflow</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Load → Chunk → Embed → Chat → Export")

    PAGES[page]()
