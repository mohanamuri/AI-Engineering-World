"""RAG Projects — UC3: Agentic RAG entry point."""

import streamlit as st
from core.launcher import go_home

from app.components.step_nav import render_page_nav, render_stepper
from applications.rag_projects.uc3.constants import NAVIGATION_SESSION_KEY
from applications.rag_projects.uc3.pages import chat, concept, configure, history, upload


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
                <div class="aiew-tier-badge-lg">UC3</div>
                <div>
                    <div class="aiew-tb-cap">RAG Projects · Use Case 3 of 4</div>
                    <div class="aiew-tb-title">Agentic RAG</div>
                    <div class="aiew-tb-desc">
                        An LLM agent decides whether to retrieve, reformulates queries when
                        context is insufficient, and iterates until it has enough information
                        to answer confidently. Every reasoning step is shown in the UI.
                    </div>
                    <div class="aiew-tb-flow">📄 Upload Docs → ⚙️ Configure → 💬 Chat → 📜 History</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">ReAct</span>
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
                "UC1 and UC2 always search ChromaDB exactly once per question — no matter "
                "whether the results are good or bad, the LLM generates an answer from whatever was found."
            )
            st.write(
                "UC3 adds a **LangGraph agent** that thinks before and after searching. "
                "It first checks: does this question even need a document search? "
                "If yes, it searches, then asks itself: are these results good enough? "
                "If not, it rephrases the question and searches again — up to a set number of tries. "
                "You can see every decision it made, directly in the chat."
            )
            st.markdown("#### New capability over UC2")
            st.info(
                "**UC2** always searches ChromaDB once with the exact question asked.\n\n"
                "**UC3** uses LangGraph to decide *whether* to search, and if the results are weak, "
                "it rephrases and tries again. Ask it a general knowledge question like "
                "'What is 2+2?' — it will skip the ChromaDB search entirely."
            )
        with col2:
            st.markdown("#### Tech stack")
            st.table({
                "Component": ["Agent framework", "Agent pattern", "Retrieval tool",
                               "Query reformulation", "Embedding model", "LLM"],
                "Technology": [
                    "LangGraph StateGraph",
                    "ReAct (Reasoning + Acting)",
                    "ChromaDB similarity search",
                    "Groq LLM rewrites query on low-confidence retrieval",
                    "all-MiniLM-L6-v2 (local, free)",
                    "Groq meta-llama/llama-4-scout-17b-16e-instruct",
                ],
            })

    with st.sidebar:
        st.markdown(
            '<div class="aiew-side-label">Agentic RAG · UC3 workflow</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Upload → Configure → Chat → History")
        st.divider()
        st.caption("🤔 Classify  ·  🔍 Retrieve  ·  📊 Evaluate")
        st.caption("✏️ Reformulate  ·  ✅ Generate")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
