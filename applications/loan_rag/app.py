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
    if st.button("← Platform home"):
        go_home()
        st.rerun()

    st.markdown(
        """
        <section class="aiew-loan-hero">
            <div class="aiew-app-icon" style="font-size:.55rem;">RAG</div>
            <div>
                <h1>Loan Eligibility Prediction</h1>
                <p>
                    Retrieval-Augmented Generation · Ground loan policy Q&amp;A in
                    real documents using ChromaDB vector search and a local Ollama LLM.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Loan RAG workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigation",
            list(PAGES.keys()),
            key=NAVIGATION_SESSION_KEY,
        )
        st.caption("Load → Chunk → Embed → Chat → Export")

    PAGES[page]()
