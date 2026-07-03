"""Configure RAG parameters and build the vector store — page 3."""

from __future__ import annotations

import streamlit as st

from applications.loan_rag.constants import (
    CHUNKS_SESSION_KEY,
    LOAD_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)
from applications.loan_rag.services.document_loader import chunk_text
from applications.loan_rag.services.rag_chain import RAGConfig
from applications.loan_rag.services.vector_store import VectorStoreResult, build_vector_store


def render() -> None:
    st.header("⚙️ Configure RAG")
    st.caption(
        "Tune chunking and retrieval parameters, then build the vector store. "
        "Rebuild whenever you change chunk size or the embedding model."
    )

    load_result = st.session_state.get(LOAD_RESULT_SESSION_KEY)
    if load_result is None:
        _render_empty_state()
        return

    current_config: RAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, RAGConfig())

    # ---- Two-column config form ------------------------------------------
    col_chunk, col_model = st.columns(2)

    with col_chunk:
        with st.container(border=True):
            st.markdown("**Chunking parameters**")
            st.caption("Changing these requires rebuilding the vector store.")
            chunk_size = st.slider(
                "Chunk size (characters)",
                min_value=128, max_value=1024, step=64,
                value=current_config.chunk_size,
                help="Larger chunks carry more context; smaller chunks improve retrieval precision.",
            )
            chunk_overlap = st.slider(
                "Chunk overlap (characters)",
                min_value=0, max_value=256, step=16,
                value=current_config.chunk_overlap,
                help="Overlap lets adjacent chunks share context at their boundaries.",
            )

    with col_model:
        with st.container(border=True):
            st.markdown("**Model parameters**")
            embedding_model = st.text_input(
                "Embedding model (Ollama)",
                value=current_config.embedding_model,
                help="Used to embed chunks and queries. Must be pulled in Ollama.",
            )
            llm_model = st.text_input(
                "LLM model (Ollama)",
                value=current_config.llm_model,
                help="Used to generate answers. Must be pulled in Ollama.",
            )
            top_k = st.slider(
                "Top-k retrieval",
                min_value=1, max_value=10, value=current_config.top_k,
                help="Number of chunks sent to the LLM as context.",
            )
            temperature = st.slider(
                "Temperature",
                min_value=0.0, max_value=1.0, step=0.05,
                value=current_config.temperature,
                help="0 = deterministic, 1 = creative. Use 0 for factual Q&A.",
            )

    new_config = RAGConfig(
        llm_model=llm_model,
        embedding_model=embedding_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        top_k=top_k,
        temperature=temperature,
    )

    st.divider()

    # ---- Chunk preview (rechunk on param change) -------------------------
    chunking_changed = (
        chunk_size != current_config.chunk_size
        or chunk_overlap != current_config.chunk_overlap
    )
    if chunking_changed:
        preview_chunks = chunk_text(load_result, chunk_size, chunk_overlap)
        st.info(
            f"New chunking will produce **{len(preview_chunks)} chunks** "
            f"(was {len(st.session_state.get(CHUNKS_SESSION_KEY, []))}). "
            "Click 'Build vector store' to apply."
        )

    # ---- Build button ----------------------------------------------------
    vs_result: VectorStoreResult | None = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs_result:
        st.success(
            f"Vector store ready — {vs_result.chunk_count} chunks embedded "
            f"with **{vs_result.embedding_model}**."
        )

    if st.button("🔨 Build vector store", type="primary", use_container_width=True):
        _build_and_store(load_result, new_config)

    if vs_result:
        st.divider()
        if st.button("→ Go to Chat", type="primary"):
            st.session_state[NAVIGATION_SESSION_KEY] = "💬 Chat"
            st.rerun()


def _build_and_store(load_result, config: RAGConfig) -> None:
    """Rechunk the document, rebuild the vector store, save both to session."""
    with st.spinner(
        f"Embedding chunks with **{config.embedding_model}** … this takes ~10–30 s."
    ):
        try:
            chunks = chunk_text(load_result, config.chunk_size, config.chunk_overlap)
            vs_result = build_vector_store(chunks, config.embedding_model)
        except Exception as exc:
            st.error(
                f"Failed to build vector store: {exc}\n\n"
                "Make sure Ollama is running (`ollama serve`) and the embedding "
                f"model is pulled (`ollama pull {config.embedding_model}`)."
            )
            return

    st.session_state[CHUNKS_SESSION_KEY] = chunks
    st.session_state[RAG_CONFIG_SESSION_KEY] = config
    st.session_state[VECTOR_STORE_SESSION_KEY] = vs_result
    st.success(
        f"Built vector store: **{vs_result.chunk_count} chunks** embedded with "
        f"**{config.embedding_model}**."
    )


def _render_empty_state() -> None:
    with st.container(border=True):
        st.warning("No document loaded.")
        if st.button("← Go to Load Policy", type="primary"):
            st.session_state[NAVIGATION_SESSION_KEY] = "📄 Load Policy"
            st.rerun()
