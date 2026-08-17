"""UC6 — Configure page. Tune CRAG parameters."""

import streamlit as st

from applications.rag_projects.services.crag import CRAGConfig
from applications.rag_projects.uc6.constants import (
    RAG_CONFIG_SESSION_KEY, VECTOR_STORE_SESSION_KEY,
)


def render() -> None:
    st.subheader("⚙️ Configure CRAG")

    vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return

    existing: CRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, CRAGConfig())

    st.write("Tune the relevance grading and Wikipedia fallback. Settings take effect immediately in Chat.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Relevance grading")
        correct_threshold = st.slider(
            "CORRECT threshold (fraction)",
            min_value=0.1, max_value=1.0, value=existing.correct_threshold, step=0.1,
            help=(
                "Minimum fraction of chunks that must be graded CORRECT to use "
                "local documents only. "
                "0.6 = at least 60% CORRECT → stay local. Below that → use Wikipedia."
            ),
        )
        top_k = st.slider(
            "Chunks to retrieve (top-k)",
            min_value=1, max_value=8, value=existing.top_k,
            help="How many chunks to retrieve and grade from ChromaDB.",
        )
        wiki_top_k = st.slider(
            "Wikipedia articles to fetch",
            min_value=1, max_value=3, value=existing.wiki_top_k,
            help="How many Wikipedia articles to fetch when local docs are insufficient.",
        )

    with col2:
        st.markdown("#### Generation")
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0, value=existing.temperature, step=0.05,
        )
        st.markdown("#### Model")
        _models = ["gemma2-9b-it", "qwen/qwen3-32b", "moonshotai/kimi-k2-instruct"]
        model = st.selectbox(
            "Groq LLM",
            _models,
            index=_models.index(existing.llm_model) if existing.llm_model in _models else 0,
        )

    if st.button("💾 Save Configuration", type="primary"):
        config = CRAGConfig(
            llm_model=model,
            top_k=top_k,
            temperature=temperature,
            correct_threshold=correct_threshold,
            wiki_top_k=wiki_top_k,
        )
        st.session_state[RAG_CONFIG_SESSION_KEY] = config
        st.success("Configuration saved. Head to **Chat** to ask questions.")

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Chunks indexed", vs.chunk_count)
    c2.metric("Documents", vs.doc_count)
    c3.metric("Embedding model", vs.embedding_model)

    st.divider()
    with st.expander("How does the grade decision work?", expanded=False):
        st.markdown(
            f"""
            After retrieving top-k chunks:

            | Condition | Decision | Source used |
            |---|---|---|
            | ≥ {correct_threshold:.0%} chunks graded CORRECT | **Local only** | Your uploaded documents |
            | ≥ {correct_threshold:.0%} chunks graded INCORRECT | **Wikipedia only** | Wikipedia REST API |
            | Everything else (mixed grades) | **Combined** | Both local + Wikipedia |

            The CORRECT threshold is **{correct_threshold:.0%}** (adjustable above).
            """
        )
