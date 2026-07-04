"""Download exports — page 6 of the loan RAG workflow."""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import streamlit as st

from applications.loan_rag.constants import (
    CHAT_HISTORY_SESSION_KEY,
    CHUNKS_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)
from applications.loan_rag.services.rag_chain import RAGConfig
from applications.loan_rag.services.vector_store import VectorStoreResult


def render() -> None:
    st.header("⬇ Download")
    st.caption(
        "Export chat history and pipeline configuration as JSON or CSV. "
        "All files are generated in-memory — no disk writes."
    )

    history: list[dict] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])
    config: RAGConfig | None = st.session_state.get(RAG_CONFIG_SESSION_KEY)
    vs_result: VectorStoreResult | None = st.session_state.get(VECTOR_STORE_SESSION_KEY)
    chunks = st.session_state.get(CHUNKS_SESSION_KEY, [])

    # ---- Summary --------------------------------------------------------
    m1, m2, m3 = st.columns(3)
    m1.metric("Q&A pairs", len(history))
    m2.metric("Chunks indexed", vs_result.chunk_count if vs_result else "—")
    m3.metric("LLM model", config.llm_model if config else "—")

    st.divider()

    col1, col2 = st.columns(2)

    # ---- Chat history JSON ----------------------------------------------
    with col1:
        with st.container(border=True):
            st.markdown("#### Chat history (JSON)")
            st.caption(
                "All Q&A pairs with their retrieved source chunks "
                "and timestamps."
            )
            if history:
                st.download_button(
                    label="Download chat_history.json",
                    data=_chat_history_json(history, config),
                    file_name="loan_rag_chat_history.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_chat_json",
                )
            else:
                st.info("Ask at least one question to enable download.")

    # ---- Chat history CSV -----------------------------------------------
    with col2:
        with st.container(border=True):
            st.markdown("#### Chat history (CSV)")
            st.caption(
                "Flat table: question, answer, number of chunks retrieved, "
                "timestamp."
            )
            if history:
                st.download_button(
                    label="Download chat_history.csv",
                    data=_chat_history_csv(history),
                    file_name="loan_rag_chat_history.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_chat_csv",
                )
            else:
                st.info("Ask at least one question to enable download.")

    col3, col4 = st.columns(2)

    # ---- Chunks CSV -----------------------------------------------------
    with col3:
        with st.container(border=True):
            st.markdown("#### Document chunks (CSV)")
            st.caption(
                "All chunks produced by the splitter: index, char count, "
                "and text content."
            )
            if chunks:
                st.download_button(
                    label="Download chunks.csv",
                    data=_chunks_csv(chunks),
                    file_name="loan_rag_chunks.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_chunks",
                )
            else:
                st.info("Load and chunk a document first.")

    # ---- Config JSON ----------------------------------------------------
    with col4:
        with st.container(border=True):
            st.markdown("#### RAG configuration (JSON)")
            st.caption(
                "Snapshot of all parameters: chunk size, overlap, "
                "models, top-k, temperature."
            )
            if config:
                st.download_button(
                    label="Download rag_config.json",
                    data=_config_json(config, vs_result),
                    file_name="loan_rag_config.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_config",
                )
            else:
                st.info("Configure RAG to enable config export.")

    # ---- Usage snippet --------------------------------------------------
    if config and history:
        st.divider()
        st.subheader("How to reproduce this session")
        st.code(
            f"""from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb

# 1. Load your document
with open("loan_policy.pdf", "rb") as f:
    from pypdf import PdfReader
    from io import BytesIO
    text = "\\n\\n".join(p.extract_text() for p in PdfReader(BytesIO(f.read())).pages)

# 2. Chunk
splitter = RecursiveCharacterTextSplitter(
    chunk_size={config.chunk_size},
    chunk_overlap={config.chunk_overlap},
)
chunks = splitter.create_documents([text])

# 3. Embed and store
embeddings = HuggingFaceEmbeddings(model_name="{config.embedding_model}")
client = chromadb.EphemeralClient()
vectorstore = Chroma.from_documents(chunks, embeddings, client=client)

# 4. Query
docs = vectorstore.similarity_search("your question here", k={config.top_k})
context = "\\n\\n".join(d.page_content for d in docs)
print(context)
""",
            language="python",
        )


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _chat_history_json(history: list[dict], config: RAGConfig | None) -> bytes:
    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "model": config.llm_model if config else "unknown",
        "embedding_model": config.embedding_model if config else "unknown",
        "top_k": config.top_k if config else "unknown",
        "qa_pairs": history,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")


def _chat_history_csv(history: list[dict]) -> bytes:
    import csv
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["#", "question", "answer", "chunks_retrieved", "timestamp"])
    for i, item in enumerate(history, 1):
        writer.writerow([
            i,
            item["query"],
            item["answer"],
            len(item["source_chunks"]),
            item["timestamp"],
        ])
    return buf.getvalue().encode("utf-8")


def _chunks_csv(chunks) -> bytes:
    import csv
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["chunk_index", "char_count", "text"])
    for i, chunk in enumerate(chunks, 1):
        writer.writerow([i, len(chunk.page_content), chunk.page_content])
    return buf.getvalue().encode("utf-8")


def _config_json(config: RAGConfig, vs_result: VectorStoreResult | None) -> bytes:
    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "llm_model": config.llm_model,
        "embedding_model": config.embedding_model,
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap,
        "top_k": config.top_k,
        "temperature": config.temperature,
        "chunks_indexed": vs_result.chunk_count if vs_result else None,
    }
    return json.dumps(payload, indent=2).encode("utf-8")
