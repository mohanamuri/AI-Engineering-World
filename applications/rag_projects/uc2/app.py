"""RAG Projects — UC2: Hybrid Search RAG entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.rag_projects.uc2.constants import NAVIGATION_SESSION_KEY
from applications.rag_projects.uc2.pages import chat, concept, configure, history, upload


PAGES = {
    "📖 Concept": concept.render,
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
        <section class="aiew-tier-banner aiew-tb--t5">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC2</div>
                <div>
                    <div class="aiew-tb-cap">RAG Projects · Use Case 2 of 4</div>
                    <div class="aiew-tb-title">Hybrid Search RAG</div>
                    <div class="aiew-tb-desc">
                        Dense vector search + BM25 keyword retrieval, fused with Reciprocal Rank Fusion.
                        Higher recall on exact terms, product codes, and technical jargon that
                        embeddings alone miss. Every retrieved chunk shows which retriever found it.
                    </div>
                    <div class="aiew-tb-flow">📄 Upload Docs → ⚙️ Configure → 💬 Chat → 📜 History</div>
                    <div>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">BM25</span>
                        <span class="aiew-tech-pill">RRF Fusion</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">all-MiniLM-L6-v2</span>
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
                "UC1 searches documents by *meaning* using ChromaDB — it finds passages that "
                "say the same thing as your question, even in different words. "
                "That works great for broad questions, but it can miss very specific things: "
                "a name, a number, an exact code, or a technical term."
            )
            st.write(
                "UC2 runs **two searches at the same time**: the same meaning-based ChromaDB search "
                "plus a BM25 keyword search (like Ctrl+F in a document). "
                "Both results are combined using **RRF (Reciprocal Rank Fusion)** — passages that "
                "appear in *both* searches get ranked higher, since they match both meaning and exact words."
            )
            st.markdown("#### New capability over UC1")
            st.info(
                "**UC1** searches by meaning only (ChromaDB).\n\n"
                "**UC2** adds BM25 keyword search and merges both results with RRF. "
                "A policy clause containing an exact figure like '23,000' or a specific term "
                "like '401(k)' will now surface reliably — even if the meaning-based search missed it."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Dense retriever", "Sparse retriever", "Fusion algorithm", "Embedding model", "LLM", "Vector store"],
                "Technology": [
                    "ChromaDB + HuggingFace all-MiniLM-L6-v2",
                    "BM25 (rank-bm25 library)",
                    "Reciprocal Rank Fusion (RRF, k=60)",
                    "all-MiniLM-L6-v2 (local, free)",
                    "Groq meta-llama/llama-4-scout-17b-16e-instruct",
                    "ChromaDB EphemeralClient (in-memory)",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Hybrid Search RAG · UC2 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Configure → Chat → History")
        st.divider()
        st.caption("🔵 Dense  ·  🟠 BM25  ·  🟢 Both")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
