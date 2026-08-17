"""UC7 — Configure page. Toggle retrieval modules on/off."""

import streamlit as st
from applications.shared.groq_models import get_available_chat_models

from applications.rag_projects.services.modular_rag import ModularRAGConfig
from applications.rag_projects.uc7.constants import (
    RAG_CONFIG_SESSION_KEY, VECTOR_STORE_SESSION_KEY,
)


def render() -> None:
    st.subheader("⚙️ Configure Modular RAG")

    vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return

    existing: ModularRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, ModularRAGConfig())

    st.write(
        "Toggle retrieval modules on or off. "
        "Try different combinations and compare results in Chat."
    )

    st.markdown("#### Retrieval modules")
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("**Module 1 — Dense**")
            st.caption("ChromaDB cosine similarity")
            use_dense = st.toggle("Enable Dense", value=existing.use_dense, key="m_dense")
            st.caption("Best for: semantic questions, paraphrase")

    with col2:
        with st.container(border=True):
            st.markdown("**Module 2 — Sparse (BM25)**")
            st.caption("Keyword ranking")
            use_sparse = st.toggle("Enable Sparse", value=existing.use_sparse, key="m_sparse")
            st.caption("Best for: exact names, technical terms")

    with col3:
        with st.container(border=True):
            st.markdown("**Module 3 — Reranker (LLM)**")
            st.caption("LLM scores each chunk 1–10")
            use_reranker = st.toggle("Enable Reranker", value=existing.use_reranker, key="m_rerank")
            st.caption("Best for: highest precision — but slowest")

    if not use_dense and not use_sparse:
        st.warning("At least one of Dense or Sparse must be enabled. Dense will be used as fallback.")

    st.divider()
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Retrieval")
        top_k = st.slider(
            "Results per module (top-k)",
            min_value=2, max_value=10, value=existing.top_k,
            help="How many chunks each active module returns before fusion.",
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0, value=existing.temperature, step=0.05,
        )

    with col_right:
        st.markdown("#### Fusion")
        rrf_k = st.slider(
            "RRF constant (k)",
            min_value=10, max_value=100, value=existing.rrf_k, step=10,
            help=(
                "The k in RRF formula: score += 1/(k + rank). "
                "Higher k → less emphasis on top-ranked items. "
                "60 is the standard value."
            ),
        )
        st.markdown("#### Model")
        if "_groq_models_cache" not in st.session_state:
            st.session_state["_groq_models_cache"] = get_available_chat_models()
        _models = st.session_state["_groq_models_cache"]
        model = st.selectbox(
            "Groq LLM",
            _models,
            index=_models.index(existing.llm_model) if existing.llm_model in _models else 0,
        )

    if st.button("💾 Save Configuration", type="primary"):
        config = ModularRAGConfig(
            llm_model=model,
            top_k=top_k,
            temperature=temperature,
            use_dense=use_dense,
            use_sparse=use_sparse,
            use_reranker=use_reranker,
            rrf_k=rrf_k,
        )
        st.session_state[RAG_CONFIG_SESSION_KEY] = config
        st.success("Configuration saved. Head to **Chat** to ask questions.")

    st.divider()
    active = [m for m, on in [("Dense", use_dense), ("Sparse", use_sparse), ("Reranker", use_reranker)] if on]
    c1, c2, c3 = st.columns(3)
    c1.metric("Active modules", len(active))
    c2.metric("Chunks indexed", vs.chunk_count)
    c3.metric("RRF k", rrf_k)

    st.divider()
    with st.expander("How does RRF fusion work?", expanded=False):
        st.markdown(
            """
            **Reciprocal Rank Fusion (RRF)** merges ranked lists from different modules:

            ```
            score(doc) = Σ  1 / (k + rank_in_list_i)
            ```

            - A document ranked **#1 by both Dense and Sparse** → high combined score
            - A document ranked **#1 by only one module** → moderate score
            - A document not found by any module → not included

            RRF is *order-based* — it doesn't care about raw scores (cosine similarity, BM25 value).
            This makes it robust: you can safely combine modules with completely different scoring scales.
            """
        )
