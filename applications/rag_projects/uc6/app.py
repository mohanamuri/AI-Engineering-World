"""RAG Projects — UC6: CRAG entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.rag_projects.uc6.constants import NAVIGATION_SESSION_KEY
from applications.rag_projects.uc6.pages import chat, concept, configure, history, upload


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
                <div class="aiew-tier-badge-lg">UC6</div>
                <div>
                    <div class="aiew-tb-cap">RAG Projects · Use Case 6 of 7</div>
                    <div class="aiew-tb-title">Corrective RAG (CRAG)</div>
                    <div class="aiew-tb-desc">
                        Every retrieved chunk is graded: CORRECT, AMBIGUOUS, or INCORRECT.
                        If local documents are insufficient, CRAG automatically fetches
                        supplementary information from Wikipedia — no API key required.
                    </div>
                    <div class="aiew-tb-flow">📄 Upload → 💬 Query → 🔍 Retrieve → 🎯 Grade → 🌐 Wikipedia if needed → ✅ Answer</div>
                    <div>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Relevance Grading</span>
                        <span class="aiew-tech-pill">Wikipedia API</span>
                        <span class="aiew-tech-pill">Adaptive Retrieval</span>
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
                "UC1–UC5 retrieve chunks and generate answers without ever asking: "
                "'Are these chunks actually useful for this question?' "
                "Bad retrieval → bad answer, with no way to detect it."
            )
            st.write(
                "CRAG adds a **correction step**: an LLM grades each retrieved chunk "
                "(CORRECT / AMBIGUOUS / INCORRECT). If the local documents are "
                "insufficient, it fetches supplementary knowledge from Wikipedia — "
                "free, no API key required — and uses that instead."
            )
            st.markdown("#### New capability over UC5")
            st.info(
                "**UC5** changes how retrieval works (graph vs similarity).\n\n"
                "**UC6** adds *correction*: it validates the retrieved content "
                "and falls back to an external knowledge source when needed. "
                "This makes RAG reliable even when your local docs don't cover the question."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Retrieval", "Grading", "Fallback source",
                               "Decision logic", "LLM"],
                "Technology": [
                    "ChromaDB vector search",
                    "Groq LLM grades each chunk CORRECT/AMBIGUOUS/INCORRECT",
                    "Wikipedia REST API (free, no key)",
                    "Local / Wikipedia / Combined based on grade fractions",
                    "Groq meta-llama/llama-4-scout-17b-16e-instruct",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">CRAG · UC6 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Configure → Chat → History")
        st.divider()
        st.caption("🟢 CORRECT  ·  🟡 AMBIGUOUS  ·  🔴 INCORRECT")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
