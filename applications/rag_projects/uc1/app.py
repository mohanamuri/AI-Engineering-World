"""RAG Projects — UC1: Multi-Document RAG entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.rag_projects.uc1.constants import NAVIGATION_SESSION_KEY
from applications.rag_projects.uc1.pages import chat, configure, history, upload


PAGES = {
    "📄 Upload Docs": upload.render,
    "⚙️ Configure": configure.render,
    "💬 Chat": chat.render,
    "📜 History": history.render,
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
                <div class="aiew-tier-badge-lg">UC1</div>
                <div>
                    <div class="aiew-tb-cap">RAG Projects · Use Case 1 of 4</div>
                    <div class="aiew-tb-title">Multi-Document RAG</div>
                    <div class="aiew-tb-desc">
                        Upload multiple documents simultaneously. All chunks are embedded into a single
                        vector store with source metadata — every answer shows which document it came from.
                        No hallucination: the LLM only uses the provided context.
                    </div>
                    <div class="aiew-tb-flow">📄 Upload Docs → ⚙️ Configure → 💬 Chat → 📜 History</div>
                    <div>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">HuggingFace</span>
                        <span class="aiew-tech-pill">llama-3.1-8b</span>
                        <span class="aiew-tech-pill">all-MiniLM-L6-v2</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Multi-Doc RAG · UC1 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Configure → Chat → History")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
