"""
UC3 — Configure page.

Tune agentic RAG parameters:
  - top_k:             chunks fetched per retrieval attempt
  - max_iterations:    how many retrieve→evaluate cycles before forcing an answer
  - context_threshold: quality score (0–10) that counts as "good enough"
  - model / temperature
"""

import streamlit as st

from applications.rag_projects.services.agentic_rag import AgentRAGConfig
from applications.rag_projects.uc3.constants import (
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)


def render() -> None:
    st.subheader("⚙️ Configure Agentic RAG")

    vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    if vs is None:
        st.warning("No vector store found. Go to **Upload Docs** first.")
        return

    existing: AgentRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, AgentRAGConfig())

    st.write("Tune agent behaviour. Settings take effect immediately in Chat.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Agent loop")
        max_iterations = st.slider(
            "Max retrieval iterations",
            min_value=1, max_value=5, value=existing.max_iterations,
            help=(
                "Maximum number of retrieve → evaluate cycles per question. "
                "After this limit the agent generates an answer with whatever context it has."
            ),
        )
        context_threshold = st.slider(
            "Context quality threshold (0–10)",
            min_value=3, max_value=9, value=existing.context_threshold,
            help=(
                "If the LLM rates retrieved context at or above this score, the agent "
                "stops iterating and generates the answer immediately. "
                "Lower = accept weaker context. Higher = more reformulation attempts."
            ),
        )
        top_k = st.slider(
            "Chunks per retrieval",
            min_value=1, max_value=10, value=existing.top_k,
            help="How many chunks to fetch from the vector store on each retrieval attempt.",
        )

    with col2:
        st.markdown("#### Generation")
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0, value=existing.temperature, step=0.05,
            help="0 = deterministic. Higher = more varied but less reliable.",
        )
        st.markdown("#### Model")
        _models = ["gemma2-9b-it", "qwen/qwen3-32b", "moonshotai/kimi-k2-instruct"]
        model = st.selectbox(
            "Groq LLM",
            _models,
            index=_models.index(existing.llm_model) if existing.llm_model in _models else 0,
            help="All models are free on Groq's API.",
        )

    if st.button("💾 Save Configuration", type="primary"):
        config = AgentRAGConfig(
            llm_model=model,
            top_k=top_k,
            temperature=temperature,
            max_iterations=max_iterations,
            context_threshold=context_threshold,
        )
        st.session_state[RAG_CONFIG_SESSION_KEY] = config
        st.success("Configuration saved. Head to **Chat** to ask questions.")

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Chunks indexed", vs.chunk_count)
    c2.metric("Documents", vs.doc_count)
    c3.metric("Embedding model", vs.embedding_model)

    st.divider()
    with st.expander("How does the agent loop work?", expanded=False):
        st.markdown(
            """
            The **LangGraph agent** follows this loop for every question:

            1. **Classify** — Should I even search the documents? (Some questions don't need it.)
            2. **Retrieve** — Search ChromaDB and fetch the top matching passages.
            3. **Evaluate** — Are these results good enough to answer the question? (Scored 0–10.)
            4. **Reformulate** — If the score is too low and tries remain, rewrite the question
               to be more specific, then go back to Retrieve.
            5. **Generate** — Write the final answer using the best passages found.

            The full trace — every decision, every query tried, every score — is shown in Chat.
            """
        )
