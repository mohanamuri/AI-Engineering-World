"""
UC2 — Chat page.

Hybrid Search RAG chat interface.
Each retrieved chunk shows a retriever badge:
  🔵 Dense  — found only by vector similarity
  🟠 BM25   — found only by keyword matching
  🟢 Both   — appeared in both ranked lists (boosted by RRF)
"""

import streamlit as st

from applications.rag_projects.services.hybrid_rag_chain import (
    HybridRAGConfig,
    HybridRAGResult,
    run_hybrid_rag_query,
)
from applications.rag_projects.uc2.constants import (
    BM25_RETRIEVER_SESSION_KEY,
    CHAT_HISTORY_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)

_RETRIEVER_BADGE = {
    "dense": "🔵 Dense",
    "bm25": "🟠 BM25",
    "both": "🟢 Both",
}

_SAMPLE_QUESTIONS = [
    "What is the maximum number of remote work days allowed per week?",
    "What health benefits are employees entitled to?",
    "What are the consequences of violating the code of conduct?",
    "Summarise the key points across all policy documents.",
]


def render() -> None:
    st.subheader("💬 Chat")

    vs_result = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    bm25 = st.session_state.get(BM25_RETRIEVER_SESSION_KEY)
    if vs_result is None or bm25 is None:
        st.warning("No indexes found. Go to **Upload Docs** first.")
        return

    config: HybridRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, HybridRAGConfig())
    history: list[HybridRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    # --- Sample questions ---
    if not history:
        st.markdown("**Try a sample question:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_QUESTIONS):
            if cols[i % 2].button(q, key=f"sample_{i}", use_container_width=True):
                _run_query(q, vs_result.vectorstore, bm25, config)
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
                _render_chunks(result)

    # --- Input ---
    query = st.chat_input("Ask a question about your documents…")
    if query:
        _run_query(query, vs_result.vectorstore, bm25, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear chat history"):
            st.session_state[CHAT_HISTORY_SESSION_KEY] = []
            st.rerun()


def _render_chunks(result: HybridRAGResult) -> None:
    """Render each hybrid result with retriever badge + RRF score."""
    for i, hr in enumerate(result.hybrid_results, 1):
        badge = _RETRIEVER_BADGE.get(hr.retriever, hr.retriever)
        src = hr.doc.metadata.get("source", "unknown")

        col_meta, col_score = st.columns([4, 1])
        with col_meta:
            st.markdown(f"**Chunk {i}** — `{src}`  {badge}")
        with col_score:
            st.caption(f"RRF: {hr.rrf_score:.4f}")

        # Rank details
        rank_parts = []
        if hr.dense_rank is not None:
            rank_parts.append(f"Dense rank #{hr.dense_rank}")
        if hr.bm25_rank is not None:
            rank_parts.append(f"BM25 rank #{hr.bm25_rank}")
        if rank_parts:
            st.caption(" · ".join(rank_parts))

        st.text(hr.doc.page_content[:400] + ("…" if len(hr.doc.page_content) > 400 else ""))
        st.divider()


def _run_query(query: str, vectorstore, bm25, config: HybridRAGConfig) -> None:
    """Execute the hybrid RAG query and append the result to chat history."""
    with st.spinner("Searching documents (dense + BM25) and generating answer…"):
        try:
            result = run_hybrid_rag_query(query, vectorstore, bm25, config)
        except Exception as exc:
            st.error(f"Query failed: {exc}")
            return

    history: list[HybridRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[CHAT_HISTORY_SESSION_KEY] = history
