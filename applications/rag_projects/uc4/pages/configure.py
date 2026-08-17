"""
UC4 — Configure page.

Tune Self-RAG parameters:
  - max_attempts:       how many generate→critique cycles before keeping the best answer
  - critique_threshold: minimum score (1–5) each dimension must reach to pass
  - top_k / model / temperature
"""

import streamlit as st

from applications.rag_projects.services.self_rag import SelfRAGConfig
from applications.rag_projects.uc4.constants import (
    RAG_CONFIG_SESSION_KEY, VECTOR_STORE_SESSION_KEY,
)


def render() -> None:
    st.subheader("⚙️ Configure Self-RAG")

    vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return

    existing: SelfRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, SelfRAGConfig())

    st.write("Tune the self-critique loop. Settings take effect immediately in Chat.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Self-critique loop")
        max_attempts = st.slider(
            "Max rewrite attempts",
            min_value=1, max_value=5, value=existing.max_attempts,
            help=(
                "How many times the pipeline can rewrite and regenerate the answer. "
                "After this limit, the last answer is kept regardless of scores."
            ),
        )
        critique_threshold = st.slider(
            "Critique threshold (1–5)",
            min_value=1, max_value=5, value=existing.critique_threshold,
            help=(
                "Each of the three dimensions (Groundedness, Relevance, Completeness) "
                "must score at or above this to pass. If any fails, the answer is rewritten. "
                "3 = balanced, 4 = strict, 5 = only accepts near-perfect answers."
            ),
        )
        top_k = st.slider(
            "Chunks per retrieval",
            min_value=1, max_value=10, value=existing.top_k,
            help="How many passages to fetch from ChromaDB for each attempt.",
        )

    with col2:
        st.markdown("#### Generation")
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0, value=existing.temperature, step=0.05,
            help="0 = deterministic. Higher = more varied but less reliable.",
        )
        st.markdown("#### Model")
        _models = ["llama-3.1-8b-instant", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
        model = st.selectbox(
            "Groq LLM",
            _models,
            index=_models.index(existing.llm_model) if existing.llm_model in _models else 0,
        )

    if st.button("💾 Save Configuration", type="primary"):
        config = SelfRAGConfig(
            llm_model=model,
            top_k=top_k,
            temperature=temperature,
            max_attempts=max_attempts,
            critique_threshold=critique_threshold,
        )
        st.session_state[RAG_CONFIG_SESSION_KEY] = config
        st.success("Configuration saved. Head to **Chat** to ask questions.")

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Chunks indexed", vs.chunk_count)
    c2.metric("Documents", vs.doc_count)
    c3.metric("Embedding model", vs.embedding_model)

    st.divider()
    with st.expander("How does the critique loop work?", expanded=False):
        st.markdown(
            """
            After generating an answer, the LangGraph agent scores it on three dimensions:

            | Dimension | What it checks |
            |---|---|
            | **Groundedness** | Is every claim in the answer backed by the retrieved passages? |
            | **Relevance** | Does the answer actually address the question? |
            | **Completeness** | Does it cover all the key points in the passages? |

            Each dimension is scored **1–5**. If any score is below the threshold,
            the pipeline rewrites the question to be more targeted, re-retrieves from ChromaDB,
            and generates a new answer — then critiques again.

            The Chat page shows a scorecard for every attempt so you can see exactly
            how the answer improved across rewrites.
            """
        )
