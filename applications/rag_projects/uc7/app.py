"""RAG Projects — UC7: Modular RAG entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.rag_projects.uc7.constants import NAVIGATION_SESSION_KEY
from applications.rag_projects.uc7.pages import chat, concept, configure, history, upload


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
        <section class="aiew-tier-banner aiew-tb--t6">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC7</div>
                <div>
                    <div class="aiew-tb-cap">RAG Projects · Use Case 7 of 7</div>
                    <div class="aiew-tb-title">Modular RAG</div>
                    <div class="aiew-tb-desc">
                        Three independent retrieval modules — Dense (ChromaDB), Sparse (BM25),
                        and Reranker (LLM) — that you can toggle on/off. Results are fused
                        with Reciprocal Rank Fusion. See exactly what each module contributes.
                    </div>
                    <div class="aiew-tb-flow">📄 Upload → ⚙️ Choose Modules → 💬 Query → Dense + BM25 + Rerank → RRF Fusion → ✅ Answer</div>
                    <div>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">BM25</span>
                        <span class="aiew-tech-pill">Groq Reranker</span>
                        <span class="aiew-tech-pill">RRF Fusion</span>
                        <span class="aiew-tech-pill">Modular Design</span>
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
                "Previous use cases used fixed retrieval pipelines. "
                "Modular RAG treats retrieval as a set of interchangeable components: "
                "Dense (vector search), Sparse (keyword search), and Reranker (LLM scoring). "
                "Toggle any combination on or off and see how each module changes the results."
            )
            st.write(
                "Results from active modules are merged using **Reciprocal Rank Fusion (RRF)** — "
                "the same technique used in UC2 but now extended to three modules. "
                "Each chunk shows which modules contributed to its ranking."
            )
            st.markdown("#### New capability over UC6")
            st.info(
                "**UC6** adds a correction/fallback mechanism.\n\n"
                "**UC7** makes the entire retrieval pipeline configurable. "
                "You can compare any combination of modules side-by-side — "
                "Dense-only vs Dense+Sparse vs Dense+Sparse+Reranker — "
                "and understand the trade-off between quality and latency."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Module 1 — Dense", "Module 2 — Sparse",
                               "Module 3 — Reranker", "Fusion", "LLM"],
                "Technology": [
                    "ChromaDB cosine-similarity search",
                    "BM25 keyword ranking (rank-bm25)",
                    "Groq LLM cross-encoder style scoring (1–10)",
                    "Reciprocal Rank Fusion (RRF, k=60)",
                    "Groq llama-3.1-8b-instant",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Modular RAG · UC7 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Configure modules → Chat → History")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
