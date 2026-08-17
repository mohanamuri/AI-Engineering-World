"""
Modular RAG service for UC7.

How it is different from UC1–UC4:
  UC1 uses one retrieval method: dense vector search (ChromaDB).
  UC2 adds BM25 keyword search and fuses both.
  UC7 goes further — it exposes three independent retrieval modules that
  the user can toggle on/off and weight individually:

    Module 1 — Dense     : ChromaDB cosine-similarity vector search
    Module 2 — Sparse    : BM25 keyword retrieval (rank-bm25)
    Module 3 — Reranker  : LLM-based cross-encoder style scoring

  Results from active modules are merged with Reciprocal Rank Fusion (RRF).
  The user sees exactly which module contributed each chunk.

Architecture:
  Each module is an independent retriever that accepts a query and returns
  ranked chunks. The coordinator runs all active modules, applies RRF fusion,
  and passes the top-k fused chunks to the LLM for generation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ModularRAGConfig:
    """Tunable parameters for Modular RAG."""
    llm_model: str = "llama-3.1-8b-instant"
    top_k: int = 5
    temperature: float = 0.0
    # Module toggles
    use_dense: bool = True
    use_sparse: bool = True
    use_reranker: bool = True
    # RRF constant (60 is the standard value)
    rrf_k: int = 60


@dataclass
class ModuleResult:
    """Ranked results from one retrieval module."""
    module_name: str
    chunks: list[Document] = field(default_factory=list)


@dataclass
class FusedChunk:
    """One chunk after RRF fusion, with module attribution."""
    chunk: Document
    rrf_score: float
    contributing_modules: list[str] = field(default_factory=list)


@dataclass
class ModularRAGResult:
    """One query–response with per-module attribution."""
    query: str
    answer: str
    module_results: list[ModuleResult] = field(default_factory=list)
    fused_chunks: list[FusedChunk] = field(default_factory=list)
    active_modules: list[str] = field(default_factory=list)
    source_names: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_groq_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


def _get_llm(config: ModularRAGConfig) -> ChatGroq:
    return ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )


def _doc_id(doc: Document) -> str:
    """Stable identity string for a document chunk (content hash)."""
    return doc.page_content[:120]


# ---------------------------------------------------------------------------
# Module 1 — Dense retrieval
# ---------------------------------------------------------------------------

def dense_retrieve(query: str, vectorstore, top_k: int) -> ModuleResult:
    """Retrieve using ChromaDB cosine-similarity vector search."""
    chunks = vectorstore.similarity_search(query, k=top_k)
    return ModuleResult(module_name="Dense", chunks=chunks)


# ---------------------------------------------------------------------------
# Module 2 — Sparse retrieval (BM25)
# ---------------------------------------------------------------------------

def sparse_retrieve(query: str, all_chunks: list[Document], top_k: int) -> ModuleResult:
    """Retrieve using BM25 keyword matching.

    Args:
        query:      Search query.
        all_chunks: All document chunks to build the BM25 index from.
        top_k:      Number of results to return.

    Returns:
        ModuleResult with BM25-ranked chunks.
    """
    retriever = BM25Retriever.from_documents(all_chunks, k=top_k)
    chunks = retriever.invoke(query)
    return ModuleResult(module_name="Sparse (BM25)", chunks=chunks)


# ---------------------------------------------------------------------------
# Module 3 — LLM reranker
# ---------------------------------------------------------------------------

def rerank_retrieve(
    query: str,
    chunks: list[Document],
    top_k: int,
    llm: ChatGroq,
) -> ModuleResult:
    """Score each candidate chunk with the LLM and return top-k by score.

    The LLM assigns a 1–10 relevance score to each chunk independently.
    This mimics a cross-encoder: each chunk is evaluated in the context
    of the full query, not just by surface similarity.

    Args:
        query:   The user question.
        chunks:  Candidate chunks to rerank (typically combined dense+sparse pool).
        top_k:   Number of chunks to return after reranking.
        llm:     Groq ChatGroq instance.

    Returns:
        ModuleResult with top-k reranked chunks.
    """
    scored: list[tuple[int, Document]] = []
    for chunk in chunks:
        resp = llm.invoke([
            SystemMessage(content=(
                "Rate how relevant this passage is for answering the question. "
                "Output ONLY a single integer from 1 (irrelevant) to 10 (perfectly relevant). "
                "Nothing else."
            )),
            HumanMessage(content=(
                f"Question: {query}\n\nPassage:\n{chunk.page_content[:500]}"
            )),
        ])
        try:
            score = int(resp.content.strip().split()[0])
        except (ValueError, IndexError):
            score = 5
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return ModuleResult(
        module_name="Reranker (LLM)",
        chunks=[c for _, c in scored[:top_k]],
    )


# ---------------------------------------------------------------------------
# RRF fusion
# ---------------------------------------------------------------------------

def reciprocal_rank_fusion(
    module_results: list[ModuleResult],
    top_k: int,
    rrf_k: int = 60,
) -> list[FusedChunk]:
    """Merge ranked lists from multiple modules using Reciprocal Rank Fusion.

    RRF score for a document d across a set of ranked lists:
        score(d) = Σ  1 / (rrf_k + rank_in_list_i)

    Docs that appear high in multiple lists get the highest combined scores.
    Docs unique to one list still appear if ranked highly in that list.

    Args:
        module_results: Ranked results from each active module.
        top_k:          Number of fused chunks to return.
        rrf_k:          RRF constant (60 is standard).

    Returns:
        List of FusedChunk sorted by descending RRF score.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}
    contributing: dict[str, list[str]] = {}

    for result in module_results:
        for rank, chunk in enumerate(result.chunks):
            doc_id = _doc_id(chunk)
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (rrf_k + rank + 1)
            doc_map[doc_id] = chunk
            contributing.setdefault(doc_id, [])
            if result.module_name not in contributing[doc_id]:
                contributing[doc_id].append(result.module_name)

    sorted_ids = sorted(scores, key=lambda d: scores[d], reverse=True)
    return [
        FusedChunk(
            chunk=doc_map[doc_id],
            rrf_score=round(scores[doc_id], 4),
            contributing_modules=contributing[doc_id],
        )
        for doc_id in sorted_ids[:top_k]
    ]


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_modular_rag_query(
    query: str,
    vectorstore,
    all_chunks: list[Document],
    config: ModularRAGConfig,
) -> ModularRAGResult:
    """Run the Modular RAG pipeline with all active modules.

    Args:
        query:       Natural language question.
        vectorstore: Pre-built ChromaDB Chroma instance (for dense module).
        all_chunks:  All document chunks (for BM25 module).
        config:      ModularRAGConfig controlling which modules are active.

    Returns:
        ModularRAGResult with per-module results, fused ranking, and the final answer.
    """
    llm = _get_llm(config)
    module_results: list[ModuleResult] = []
    active_modules: list[str] = []

    # Run active modules
    if config.use_dense:
        module_results.append(dense_retrieve(query, vectorstore, config.top_k))
        active_modules.append("Dense")

    if config.use_sparse and all_chunks:
        module_results.append(sparse_retrieve(query, all_chunks, config.top_k))
        active_modules.append("Sparse (BM25)")

    if not module_results:
        # No modules active — fall back to dense only
        module_results.append(dense_retrieve(query, vectorstore, config.top_k))
        active_modules.append("Dense (fallback)")

    # Collect candidate pool for reranker
    candidate_pool: list[Document] = []
    seen_ids: set[str] = set()
    for mr in module_results:
        for chunk in mr.chunks:
            did = _doc_id(chunk)
            if did not in seen_ids:
                seen_ids.add(did)
                candidate_pool.append(chunk)

    if config.use_reranker and candidate_pool:
        reranked = rerank_retrieve(query, candidate_pool, config.top_k, llm)
        module_results.append(reranked)
        active_modules.append("Reranker (LLM)")

    # RRF fusion
    fused = reciprocal_rank_fusion(module_results, top_k=config.top_k, rrf_k=config.rrf_k)

    # Generate answer
    context = "\n\n---\n\n".join(
        f"[{i + 1}] (source: {fc.chunk.metadata.get('source', 'unknown')} "
        f"| modules: {', '.join(fc.contributing_modules)})\n{fc.chunk.page_content}"
        for i, fc in enumerate(fused)
    )
    ans_resp = llm.invoke([
        SystemMessage(content=(
            "You are a precise document assistant. "
            "Answer the question using ONLY the provided context. "
            "Be concise and factual."
        )),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"),
    ])

    source_names = list(dict.fromkeys(
        fc.chunk.metadata.get("source", "unknown") for fc in fused
    ))

    return ModularRAGResult(
        query=query,
        answer=ans_resp.content.strip(),
        module_results=module_results,
        fused_chunks=fused,
        active_modules=active_modules,
        source_names=source_names,
    )
