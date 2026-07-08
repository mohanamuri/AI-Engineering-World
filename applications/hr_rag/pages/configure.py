"""Configure RAG — page 3 of the HR RAG workflow."""

from __future__ import annotations
import streamlit as st

from applications.hr_rag.constants import (
    CHUNKS_SESSION_KEY, LOAD_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY, RAG_CONFIG_SESSION_KEY, VECTOR_STORE_SESSION_KEY,
)
from applications.hr_rag.services.document_loader import chunk_text
from applications.hr_rag.services.rag_chain import RAGConfig
from applications.hr_rag.services.vector_store import VectorStoreResult, build_vector_store
from applications.shared.api_reference import render_api_reference


def render() -> None:
    st.header("⚙️ Configure RAG")
    st.caption("Tune chunking and retrieval parameters, then build the vector store.")

    load_result = st.session_state.get(LOAD_RESULT_SESSION_KEY)
    if load_result is None:
        st.warning("Load a policy document first.")
        st.button("← Go to Load Policy", type="primary",
                  on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: "📄 Load Policy"}))
        return

    current_config = st.session_state.get(RAG_CONFIG_SESSION_KEY, RAGConfig())

    col_chunk, col_model = st.columns(2)
    with col_chunk:
        with st.container(border=True):
            st.markdown("**Chunking parameters**")
            chunk_size = st.slider("Chunk size (chars)", 128, 1024, current_config.chunk_size, 64)
            chunk_overlap = st.slider("Chunk overlap (chars)", 0, 256, current_config.chunk_overlap, 16)

    with col_model:
        with st.container(border=True):
            st.markdown("**Model parameters**")
            embedding_model = st.text_input("Embedding model (HuggingFace)", current_config.embedding_model)
            llm_model = st.text_input("LLM model (Groq)", current_config.llm_model)
            top_k = st.slider("Top-k retrieval", 1, 10, current_config.top_k)
            temperature = st.slider("Temperature", 0.0, 1.0, current_config.temperature, 0.05)

    new_config = RAGConfig(llm_model=llm_model, embedding_model=embedding_model,
                           chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                           top_k=top_k, temperature=temperature)

    st.divider()
    vs_result = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs_result:
        st.success(f"Vector store ready — {vs_result.chunk_count} chunks embedded with **{vs_result.embedding_model}**.")

    if st.button("🔨 Build vector store", type="primary", use_container_width=True):
        with st.spinner(f"Embedding with **{new_config.embedding_model}** … (~10–30 s)"):
            try:
                chunks = chunk_text(load_result, chunk_size, chunk_overlap)
                vs = build_vector_store(chunks, embedding_model)
            except Exception as exc:
                st.error(f"Failed: {exc}")
                return
        st.session_state[CHUNKS_SESSION_KEY] = chunks
        st.session_state[RAG_CONFIG_SESSION_KEY] = new_config
        st.session_state[VECTOR_STORE_SESSION_KEY] = vs
        st.success(f"Built: **{vs.chunk_count} chunks** embedded.")

    if vs_result:
        st.button("→ Go to Chat", type="primary",
                  on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: "💬 Chat"}))
    render_api_reference("hr_rag", "configure")
