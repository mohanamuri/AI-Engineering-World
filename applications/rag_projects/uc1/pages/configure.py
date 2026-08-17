"""
UC1 — Configure page.

Let the user tune RAG parameters: model, retrieval top-k, and temperature.
Settings are saved to session state and picked up by the Chat page.
"""

import streamlit as st

from applications.rag_projects.services.rag_chain import RAGConfig
from applications.rag_projects.uc1.constants import (
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)


def render() -> None:
    st.subheader("⚙️ Configure RAG")

    vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return

    existing: RAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, RAGConfig())

    st.write("Tune retrieval and generation parameters. Settings take effect immediately in Chat.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Retrieval")
        top_k = st.slider(
            "Top-k chunks to retrieve",
            min_value=1, max_value=10, value=existing.top_k,
            help="How many chunks to fetch from the vector store per question. Higher = more context but more tokens.",
        )

    with col2:
        st.markdown("#### Generation")
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0, value=existing.temperature, step=0.05,
            help="0 = deterministic answers. Higher = more varied but less reliable.",
        )

    st.markdown("#### Model")
    model = st.selectbox(
        "Groq LLM",
        ["mixtral-8x7b-32768", "mixtral-8x7b-32768", "mixtral-8x7b-32768"],
        index=["mixtral-8x7b-32768", "mixtral-8x7b-32768", "mixtral-8x7b-32768"].index(
            existing.llm_model
        ) if existing.llm_model in ["mixtral-8x7b-32768", "mixtral-8x7b-32768", "mixtral-8x7b-32768"] else 0,
        help="All models are free on Groq's API. Larger models are slower but more capable.",
    )

    if st.button("💾 Save Configuration", type="primary"):
        config = RAGConfig(llm_model=model, top_k=top_k, temperature=temperature)
        st.session_state[RAG_CONFIG_SESSION_KEY] = config
        st.success("Configuration saved. Head to **Chat** to ask questions.")

    st.divider()
    st.markdown("#### Current Vector Store")
    col1, col2, col3 = st.columns(3)
    col1.metric("Chunks indexed", vs.chunk_count)
    col2.metric("Documents", vs.doc_count)
    col3.metric("Embedding model", vs.embedding_model)
