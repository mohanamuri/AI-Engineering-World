"""
Hybrid RAG query chain for UC2 — Hybrid Search RAG.

Extends the basic RAG chain with:
  - HybridRAGConfig: adds rrf_k and top_k_per_retriever tuning knobs
  - run_hybrid_rag_query: uses hybrid_search (BM25 + dense + RRF) instead of
    a plain similarity_search, then passes fused chunks to the LLM

The result carries full retriever attribution per chunk so the UI can show
🔵 Dense / 🟠 BM25 / 🟢 Both badges.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from applications.rag_projects.services.hybrid_retriever import (
    BM25Retriever,
    HybridResult,
    hybrid_search,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class HybridRAGConfig:
    """Tunable parameters for Hybrid Search RAG."""
    llm_model: str = "llama-3.1-8b-instant"
    top_k: int = 4            # number of final fused chunks to pass to LLM
    rrf_k: int = 60           # RRF damping constant (paper default)
    temperature: float = 0.0


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class HybridRAGResult:
    """One query–response pair with hybrid retriever attribution."""
    query: str
    answer: str
    hybrid_results: list[HybridResult] = field(default_factory=list)
    source_names: list[str] = field(default_factory=list)
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

def run_hybrid_rag_query(
    query: str,
    vectorstore,
    bm25_retriever: BM25Retriever,
    config: HybridRAGConfig,
) -> HybridRAGResult:
    """Run hybrid (BM25 + dense + RRF) retrieval and generate an answer.

    Args:
        query:          Natural language question from the user.
        vectorstore:    Built Chroma instance.
        bm25_retriever: BM25Retriever built from the same chunks.
        config:         HybridRAGConfig with model and retrieval parameters.

    Returns:
        HybridRAGResult with answer, fused chunks, and retriever attribution.
    """
    # Hybrid retrieval
    hybrid_results: list[HybridResult] = hybrid_search(
        query=query,
        vectorstore=vectorstore,
        bm25_retriever=bm25_retriever,
        top_k=config.top_k,
        rrf_k=config.rrf_k,
    )

    # Build context and collect unique source names
    context_parts = []
    seen_sources: list[str] = []
    for i, hr in enumerate(hybrid_results, 1):
        source = hr.doc.metadata.get("source", "unknown")
        context_parts.append(f"[{i}] (source: {source})\n{hr.doc.page_content}")
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

    return HybridRAGResult(
        query=query,
        answer=response.content.strip(),
        hybrid_results=hybrid_results,
        source_names=seen_sources,
    )
