"""RAG Projects — UC3: Agentic RAG entry point."""

import streamlit as st
from core.launcher import go_home

from applications.rag_projects.uc3.constants import NAVIGATION_SESSION_KEY
from applications.rag_projects.uc3.pages import chat, configure, history, upload


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
                "In UC1 and UC2 the RAG pipeline is **passive** — it always retrieves exactly once, "
                "returns the top-k chunks, and hands everything to the LLM regardless of whether "
                "the context is actually sufficient to answer the question."
            )
            st.write(
                "Agentic RAG replaces the fixed pipeline with a **LangGraph agent loop**: "
                "the agent first decides if retrieval is even needed. If it retrieves but the "
                "context is weak, it reformulates the query and retrieves again. "
                "It only generates a final answer when confident the context is sufficient — "
                "or after a maximum number of iterations."
            )
            st.markdown("#### New capability over UC2")
            st.info(
                "**UC2** always retrieves once with a fixed query.\n\n"
                "**UC3** retrieves adaptively — zero times (if the LLM already knows), "
                "once (if context is sufficient), or multiple times with reformulated queries "
                "(if the first retrieval was weak). The agent's reasoning trace is shown in the UI."
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
                    "Groq llama-3.1-8b-instant",
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

    PAGES[page]()
