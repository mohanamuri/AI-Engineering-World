"""
UC7 — Chat page.

Modular RAG chat interface. After each answer shows:
- Which modules were active
- Per-module ranked results
- RRF fused chunk list with module attribution and scores
"""

import streamlit as st

from applications.rag_projects.services.modular_rag import (
    ModularRAGConfig, ModularRAGResult, run_modular_rag_query,
)
from applications.rag_projects.uc7.constants import (
    CHAT_HISTORY_SESSION_KEY,
    CHUNKS_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)

_SAMPLE_QUESTIONS = [
    "What is the remote work policy?",
    "What health benefits are employees entitled to?",
    "Summarise the code of conduct rules.",
    "What are the consequences of violating company policy?",
]


def render() -> None:
    st.subheader("💬 Chat")

    vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    chunks = st.session_state.get(CHUNKS_SESSION_KEY, [])

    if vs is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return

    config: ModularRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, ModularRAGConfig())
    history: list[ModularRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    # Show active modules
    active = [m for m, on in [
        ("Dense", config.use_dense),
        ("Sparse (BM25)", config.use_sparse),
        ("Reranker (LLM)", config.use_reranker),
    ] if on]
    st.caption(f"Active modules: **{' + '.join(active) if active else 'Dense (fallback)'}**")

    if not history:
        st.markdown("**Try a sample question:**")
        cols = st.columns(2)
        for i, q in enumerate(_SAMPLE_QUESTIONS):
            if cols[i % 2].button(q, key=f"mod_sample_{i}", use_container_width=True):
                _run_query(q, vs, chunks, config)
                st.rerun()
        st.divider()

    for result in history:
        with st.chat_message("user"):
            st.write(result.query)
        with st.chat_message("assistant"):
            st.write(result.answer)
            if result.source_names:
                st.caption("**Sources:** " + "  ·  ".join(f"`{s}`" for s in result.source_names))
            st.caption(f"Modules used: **{' + '.join(result.active_modules)}**")

            with st.expander("Per-module results", expanded=False):
                for mr in result.module_results:
                    st.markdown(f"**{mr.module_name}** — {len(mr.chunks)} chunk(s)")
                    for i, chunk in enumerate(mr.chunks):
                        src = chunk.metadata.get("source", "unknown")
                        preview = chunk.page_content[:100].replace("\n", " ")
                        st.caption(f"  #{i+1} [{src}] {preview}…")

            with st.expander("RRF fused ranking", expanded=False):
                st.markdown("**Chunks after Reciprocal Rank Fusion (highest score first):**")
                for i, fc in enumerate(result.fused_chunks):
                    src = fc.chunk.metadata.get("source", "unknown")
                    modules = ", ".join(fc.contributing_modules)
                    preview = fc.chunk.page_content[:100].replace("\n", " ")
                    st.markdown(
                        f"**#{i+1}** · RRF score: `{fc.rrf_score}` · modules: `{modules}` · source: `{src}`"
                    )
                    st.caption(preview + "…")

    query = st.chat_input("Ask a question about your documents…")
    if query:
        _run_query(query, vs, chunks, config)
        st.rerun()

    if history:
        if st.button("🗑 Clear chat history"):
            st.session_state[CHAT_HISTORY_SESSION_KEY] = []
            st.rerun()


def _run_query(query: str, vectorstore, all_chunks, config: ModularRAGConfig) -> None:
    with st.spinner("Running retrieval modules and generating answer…"):
        try:
            result = run_modular_rag_query(query, vectorstore, all_chunks, config)
        except Exception as exc:
            st.error(f"Modular RAG failed: {exc}")
            return
    history: list = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    history.append(result)
    st.session_state[CHAT_HISTORY_SESSION_KEY] = history
