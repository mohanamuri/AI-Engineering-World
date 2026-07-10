"""
UC1 — Chat page.

The core Multi-Document RAG experience:
  - Ask a natural-language question.
  - The retriever fetches the top-k most relevant chunks from ALL uploaded docs.
  - Groq LLM generates an answer grounded strictly in those chunks.
  - The UI shows the answer AND which documents contributed to it.
"""

import streamlit as st

from applications.rag_projects.services.rag_chain import RAGConfig, RAGResult, run_rag_query
from applications.rag_projects.uc1.constants import (
    CHAT_HISTORY_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)

_SAMPLE_QUESTIONS = [
    "What are the main topics covered across all documents?",
    "Summarise the key points from each document.",
    "Are there any contradictions or agreements between the documents?",
    "What recommendations do the documents make?",
]


def render() -> None:
    st.subheader("💬 Chat")

    vs_result = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs_result is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return

    config: RAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, RAGConfig())
    history: list[RAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    # --- Sample questions ---
    if not history:
        st.markdown("**Try a sample question:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_QUESTIONS):
            if cols[i % 2].button(q, key=f"sample_{i}", use_container_width=True):
                _run_query(q, vs_result.vectorstore, config)
                st.rerun()
        st.divider()

    # --- Chat history ---
    for result in history:
        with st.chat_message("user"):
            st.write(result.query)
        with st.chat_message("assistant"):
            st.write(result.answer)
            if result.source_names:
                source_label = "  ·  ".join(f"`{s}`" for s in result.source_names)
                st.caption(f"**Sources:** {source_label}")
            with st.expander("View retrieved chunks", expanded=False):
                for i, chunk in enumerate(result.source_chunks, 1):
                    src = chunk.metadata.get("source", "unknown")
                    st.markdown(f"**Chunk {i}** — `{src}`")
                    st.text(chunk.page_content[:400] + ("…" if len(chunk.page_content) > 400 else ""))
                    st.divider()

    # --- Input ---
    query = st.chat_input("Ask a question about your documents…")
    if query:
        _run_query(query, vs_result.vectorstore, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear chat history"):
            st.session_state[CHAT_HISTORY_SESSION_KEY] = []
            st.rerun()


def _run_query(query: str, vectorstore, config: RAGConfig) -> None:
    """Execute the RAG query and append the result to chat history."""
    with st.spinner("Searching documents and generating answer…"):
        try:
            result = run_rag_query(query, vectorstore, config)
        except Exception as exc:
            st.error(f"Query failed: {exc}")
            return

    history: list[RAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[CHAT_HISTORY_SESSION_KEY] = history
