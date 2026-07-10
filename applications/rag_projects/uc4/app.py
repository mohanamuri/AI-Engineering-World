"""RAG Projects — UC4: Self-RAG entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.rag_projects.uc4.constants import NAVIGATION_SESSION_KEY
from applications.rag_projects.uc4.pages import chat, configure, history, upload


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
        <section class="aiew-tier-banner aiew-tb--t6">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">UC4</div>
                <div>
                    <div class="aiew-tb-cap">RAG Projects · Use Case 4 of 4</div>
                    <div class="aiew-tb-title">Self-RAG</div>
                    <div class="aiew-tb-desc">
                        After generating an answer, the LLM scores it on Groundedness,
                        Relevance, and Completeness. If any score is too low, it rewrites
                        the query, re-retrieves, and tries again. The critique scorecard
                        is shown for every attempt.
                    </div>
                    <div class="aiew-tb-flow">📄 Upload → 💬 Query → ✍️ Generate → 🔍 Critique → 🔄 Rewrite if needed → ✅ Final Answer</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Self-Reflection</span>
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
                "UC1, UC2, and UC3 all generate an answer and stop — they never ask "
                "whether the answer is actually good."
            )
            st.write(
                "UC4 adds a **self-critique step** after every answer. "
                "The LLM reads its own answer and scores it on three things: "
                "Is every claim supported by the documents? Does it answer the actual question? "
                "Is anything important missing? "
                "If any score is too low, it rewrites the search query, fetches new passages, "
                "and tries again — showing you a scorecard for each attempt."
            )
            st.markdown("#### New capability over UC3")
            st.info(
                "**UC3** decides when and how to search (retrieval quality).\n\n"
                "**UC4** decides when the *answer itself* is good enough (generation quality). "
                "It is the only use case where the LLM explicitly judges and rewrites its own output."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Agent framework", "Critique mechanism",
                               "Critique dimensions", "Rewrite strategy",
                               "Embedding model", "LLM"],
                "Technology": [
                    "LangGraph StateGraph",
                    "Separate Groq LLM call scores each dimension 1–5",
                    "Groundedness · Relevance · Completeness",
                    "Rewrite query + re-retrieve + regenerate on low scores",
                    "all-MiniLM-L6-v2 (local, free)",
                    "Groq llama-3.1-8b-instant",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Self-RAG · UC4 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Configure → Chat → History")
        st.divider()
        st.caption("🟢 Pass  ·  🟡 Borderline  ·  🔴 Fail")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
