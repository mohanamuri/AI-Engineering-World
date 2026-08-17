"""RAG Projects — UC5: GraphRAG entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.rag_projects.uc5.constants import NAVIGATION_SESSION_KEY
from applications.rag_projects.uc5.pages import chat, concept, configure, history, upload


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
                <div class="aiew-tier-badge-lg">UC5</div>
                <div>
                    <div class="aiew-tb-cap">RAG Projects · Use Case 5 of 7</div>
                    <div class="aiew-tb-title">GraphRAG</div>
                    <div class="aiew-tb-desc">
                        LLM extracts entities and relationships from your documents to build
                        a Knowledge Graph. Answers are found by traversing the graph —
                        discovering connected information that simple similarity search misses.
                    </div>
                    <div class="aiew-tb-flow">📄 Upload → 🕸️ Build Graph → ⚙️ Configure → 💬 Query → Graph Traversal → ✅ Answer</div>
                    <div>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Knowledge Graph</span>
                        <span class="aiew-tech-pill">Entity Extraction</span>
                        <span class="aiew-tech-pill">BFS Traversal</span>
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
                "UC1–UC4 find chunks that are *similar* to your question — "
                "they match words and meaning. But some answers require following "
                "relationships: 'Who manages the team that handles X?' needs to "
                "know *who manages who*, not just similarity."
            )
            st.write(
                "GraphRAG builds a **Knowledge Graph** — a map of entities (people, "
                "policies, processes) and how they connect. When you ask a question, "
                "it finds relevant entities and follows their relationships to "
                "discover connected information."
            )
            st.markdown("#### New capability over UC4")
            st.info(
                "**UC4** evaluates whether its own answer is good.\n\n"
                "**UC5** changes *how* information is retrieved — by following "
                "entity relationships in a graph rather than similarity matching. "
                "It finds answers that have low keyword overlap with the question."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Graph structure", "Entity extraction",
                               "Graph traversal", "Retrieval", "LLM"],
                "Technology": [
                    "In-memory dict graph (no extra library)",
                    "Groq LLM extracts (entity, relation, entity) triples",
                    "BFS up to max_hops",
                    "Entity → chunk index mapping",
                    "Groq mixtral-8x7b-32768",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">GraphRAG · UC5 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Configure → Chat → History")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
