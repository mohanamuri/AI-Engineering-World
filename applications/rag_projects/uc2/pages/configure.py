"""
UC2 — Configure page.

Tune hybrid retrieval parameters:
  - top_k:        number of fused chunks passed to the LLM
  - rrf_k:        RRF damping constant (default 60, per the original paper)
  - model:        Groq LLM
  - temperature:  generation randomness

RRF explanation is shown inline so users understand what they're tuning.
"""

import streamlit as st
from applications.shared.groq_models import get_available_chat_models

from applications.rag_projects.services.hybrid_rag_chain import HybridRAGConfig
from applications.rag_projects.uc2.constants import (
    BM25_RETRIEVER_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)


def render() -> None:
    st.subheader("⚙️ Configure Hybrid RAG")

    vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    bm25 = st.session_state.get(BM25_RETRIEVER_SESSION_KEY)
    if vs is None or bm25 is None:
        st.warning("No indexes found. Go to **Upload Docs** first.")
        return

    existing: HybridRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, HybridRAGConfig())

    st.write("Tune hybrid retrieval and generation parameters. Settings take effect immediately in Chat.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Retrieval")
        top_k = st.slider(
            "Final top-k chunks (after RRF fusion)",
            min_value=1, max_value=10, value=existing.top_k,
            help=(
                "How many fused chunks to pass to the LLM. Each retriever fetches 2× this "
                "number as candidates, then RRF picks the best top_k."
            ),
        )
        rrf_k = st.slider(
            "RRF damping constant (k)",
            min_value=10, max_value=120, value=existing.rrf_k, step=10,
            help=(
                "RRF score = Σ 1/(rank + k). Higher k dampens the advantage of top-ranked "
                "results, making the fusion more balanced. Default 60 is the paper's recommendation."
            ),
        )

    with col2:
        st.markdown("#### Generation")
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0, value=existing.temperature, step=0.05,
            help="0 = deterministic answers. Higher = more varied but less reliable.",
        )

    st.markdown("#### Model")
    if "_groq_models_cache" not in st.session_state:
        st.session_state["_groq_models_cache"] = get_available_chat_models()
    _models = st.session_state["_groq_models_cache"]
    model = st.selectbox(
        "Groq LLM",
        _models,
        index=_models.index(existing.llm_model) if existing.llm_model in _models else 0,
        help="All models are free on Groq's API. Larger models are slower but more capable.",
    )

    if st.button("💾 Save Configuration", type="primary"):
        config = HybridRAGConfig(
            llm_model=model,
            top_k=top_k,
            rrf_k=rrf_k,
            temperature=temperature,
        )
        st.session_state[RAG_CONFIG_SESSION_KEY] = config
        st.success("Configuration saved. Head to **Chat** to ask questions.")

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Chunks indexed", vs.chunk_count)
    col2.metric("Documents", vs.doc_count)
    col3.metric("BM25 index", "Ready")

    st.divider()
    with st.expander("How does RRF fusion work?", expanded=False):
        st.markdown(
            """
            **Reciprocal Rank Fusion (RRF)** is a simple way to combine two ranked lists
            without needing their scores to be on the same scale.

            Each passage gets a contribution from every ranked list it appears in:

            > **score = Σ 1 / (rank + k)**

            - A passage ranked #1 by ChromaDB and #3 by BM25 scores higher than one that
              only appears in one list.
            - The constant **k** (default 60) smooths out the scores so that being ranked
              #1 in one list doesn't completely dominate the result.
            - After combining, the top-k highest-scoring passages are sent to the LLM.
            """
        )
