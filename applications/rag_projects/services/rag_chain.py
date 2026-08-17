"""
RAG query chain for RAG Projects.

Adds one capability on top of the loan_rag chain:
  - Returns source_names (unique document names that contributed chunks)
    so the UI can clearly attribute each answer to its source documents.

This matters in multi-document RAG: the user uploaded 3 documents — after
asking a question they need to know *which* document (or documents) the
answer came from.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class RAGConfig:
    """Tunable RAG parameters."""
    llm_model: str = "gemma2-9b-it"
    top_k: int = 4
    temperature: float = 0.0


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class RAGResult:
    """One query–response pair with full source attribution."""
    query: str
    answer: str
    source_chunks: list[Document] = field(default_factory=list)
    source_names: list[str] = field(default_factory=list)   # unique doc names used
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Groq key helper
# ---------------------------------------------------------------------------

def _get_groq_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a precise document assistant.
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say "I could not find this in the provided documents."

Rules:
- Be factual and concise.
- Do not fabricate information.
- If multiple documents are relevant, synthesise them coherently.
- Always refer to the context, not general knowledge.
"""


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_rag_query(
    query: str,
    vectorstore,
    config: RAGConfig,
) -> RAGResult:
    """Retrieve top-k chunks then generate an answer with Groq.

    Args:
        query:       Natural language question from the user.
        vectorstore: Built Chroma instance (from vector_store.build_vector_store).
        config:      RAGConfig with model and retrieval parameters.

    Returns:
        RAGResult with answer, source chunks, and unique source document names.
    """
    # Retrieve relevant chunks
    chunks = vectorstore.similarity_search(query, k=config.top_k)

    # Build context string and collect unique source names
    context_parts = []
    seen_sources: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.metadata.get("source", "unknown")
        context_parts.append(f"[{i}] (source: {source})\n{chunk.page_content}")
        if source not in seen_sources:
            seen_sources.append(source)

    context = "\n\n---\n\n".join(context_parts)

    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Context from documents:\n\n{context}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )),
    ]

    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    response = llm.invoke(messages)

    return RAGResult(
        query=query,
        answer=response.content.strip(),
        source_chunks=chunks,
        source_names=seen_sources,
    )
