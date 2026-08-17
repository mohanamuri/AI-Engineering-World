"""
Corrective RAG (CRAG) service for UC6.

How it is different from UC1–UC4:
  UC1–UC4 trust the retrieved chunks — they never check whether the chunks
  are actually relevant to the question.
  CRAG adds a *relevance grading step*: the LLM evaluates each retrieved chunk
  and classifies it as CORRECT, AMBIGUOUS, or INCORRECT.
  Based on those grades, it decides how to proceed:
    - Most chunks CORRECT   → answer from local docs only
    - Mixed CORRECT/AMBIGUOUS → combine local docs with Wikipedia supplement
    - Most chunks INCORRECT  → ignore local docs, use Wikipedia only

Wikipedia is called via the free REST API — no API key required.

Pipeline:
    retrieve → grade chunks → decide source → (fetch Wikipedia if needed) → generate
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

import requests
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class RelevanceGrade(str, Enum):
    CORRECT = "CORRECT"
    AMBIGUOUS = "AMBIGUOUS"
    INCORRECT = "INCORRECT"


class SourceDecision(str, Enum):
    LOCAL = "Local Documents"
    WIKIPEDIA = "Wikipedia"
    COMBINED = "Local + Wikipedia"


@dataclass
class ChunkGrade:
    """Grade for one retrieved chunk."""
    chunk_idx: int
    grade: RelevanceGrade
    reason: str


@dataclass
class CRAGConfig:
    """Tunable parameters for CRAG."""
    llm_model: str = "openai/gpt-oss-20b"
    top_k: int = 4
    temperature: float = 0.0
    # Fraction of CORRECT chunks needed to stay local-only (0.0-1.0)
    correct_threshold: float = 0.6
    # Max Wikipedia passages to fetch
    wiki_top_k: int = 2


@dataclass
class WikiPassage:
    """One Wikipedia article passage."""
    title: str
    extract: str
    url: str


@dataclass
class CRAGResult:
    """One query–response with full CRAG trace."""
    query: str
    answer: str
    source_decision: SourceDecision
    chunk_grades: list[ChunkGrade] = field(default_factory=list)
    local_chunks: list[Document] = field(default_factory=list)
    wiki_passages: list[WikiPassage] = field(default_factory=list)
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


def _get_llm(config: CRAGConfig) -> ChatGroq:
    return ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )


# ---------------------------------------------------------------------------
# Relevance grading
# ---------------------------------------------------------------------------

def grade_chunk(query: str, chunk: Document, chunk_idx: int, llm: ChatGroq) -> ChunkGrade:
    """Ask the LLM to grade one chunk's relevance to the query.

    Returns a ChunkGrade with grade CORRECT | AMBIGUOUS | INCORRECT.
    """
    response = llm.invoke([
        SystemMessage(content=(
            "You are a relevance evaluator. Given a question and a text passage, "
            "classify how useful the passage is for answering the question.\n\n"
            "Respond in EXACTLY this format (two lines, no extra text):\n"
            "GRADE: CORRECT\n"
            "REASON: <one sentence>\n\n"
            "Grade meanings:\n"
            "  CORRECT   — passage directly addresses the question\n"
            "  AMBIGUOUS — passage is related but only partially helpful\n"
            "  INCORRECT — passage is off-topic or irrelevant"
        )),
        HumanMessage(content=(
            f"Question: {query}\n\n"
            f"Passage:\n{chunk.page_content[:600]}"
        )),
    ])

    text = response.content.strip()
    grade = RelevanceGrade.AMBIGUOUS
    reason = "Could not parse grade."

    for line in text.split("\n"):
        if line.upper().startswith("GRADE:"):
            raw = line.split(":", 1)[1].strip().upper()
            if "CORRECT" in raw and "INCORRECT" not in raw:
                grade = RelevanceGrade.CORRECT
            elif "INCORRECT" in raw:
                grade = RelevanceGrade.INCORRECT
            else:
                grade = RelevanceGrade.AMBIGUOUS
        elif line.upper().startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()

    return ChunkGrade(chunk_idx=chunk_idx, grade=grade, reason=reason)


# ---------------------------------------------------------------------------
# Wikipedia fallback
# ---------------------------------------------------------------------------

_WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
_WIKI_TIMEOUT = 8  # seconds


def search_wikipedia(query: str, top_k: int = 2) -> list[WikiPassage]:
    """Search Wikipedia and return short article extracts.

    Uses the Wikipedia REST API — no API key required.

    Args:
        query:  Natural language search query.
        top_k:  Max number of articles to return.

    Returns:
        List of WikiPassage with title, extract, and URL.
    """
    passages: list[WikiPassage] = []

    try:
        # Step 1: search for matching article titles
        search_resp = requests.get(
            _WIKI_SEARCH_URL,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": top_k,
            },
            timeout=_WIKI_TIMEOUT,
        )
        search_resp.raise_for_status()
        results = search_resp.json().get("query", {}).get("search", [])

        for item in results[:top_k]:
            title = item.get("title", "")
            if not title:
                continue
            # Step 2: get article extract
            extract_resp = requests.get(
                _WIKI_SEARCH_URL,
                params={
                    "action": "query",
                    "titles": title,
                    "prop": "extracts",
                    "exintro": 1,
                    "explaintext": 1,
                    "format": "json",
                },
                timeout=_WIKI_TIMEOUT,
            )
            extract_resp.raise_for_status()
            pages = extract_resp.json().get("query", {}).get("pages", {})
            for page in pages.values():
                extract = page.get("extract", "").strip()
                if extract:
                    passages.append(WikiPassage(
                        title=title,
                        extract=extract[:1200],
                        url=f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                    ))

    except Exception:
        pass  # Wikipedia unavailable — fallback silently

    return passages


# ---------------------------------------------------------------------------
# CRAG runner
# ---------------------------------------------------------------------------

def run_crag_query(
    query: str,
    vectorstore,
    config: CRAGConfig,
) -> CRAGResult:
    """Run the full CRAG pipeline.

    Args:
        query:       Natural language question.
        vectorstore: Pre-built ChromaDB Chroma instance.
        config:      CRAGConfig with thresholds and model settings.

    Returns:
        CRAGResult with answer, source decision, grades, and Wikipedia passages.
    """
    llm = _get_llm(config)

    # 1. Retrieve from local vector store
    local_chunks: list[Document] = vectorstore.similarity_search(query, k=config.top_k)

    # 2. Grade each chunk
    grades = [grade_chunk(query, chunk, i, llm) for i, chunk in enumerate(local_chunks)]

    # 3. Decide source based on grades
    n_correct = sum(1 for g in grades if g.grade == RelevanceGrade.CORRECT)
    n_incorrect = sum(1 for g in grades if g.grade == RelevanceGrade.INCORRECT)
    total = max(len(grades), 1)

    correct_frac = n_correct / total
    incorrect_frac = n_incorrect / total

    if correct_frac >= config.correct_threshold:
        decision = SourceDecision.LOCAL
    elif incorrect_frac >= config.correct_threshold:
        decision = SourceDecision.WIKIPEDIA
    else:
        decision = SourceDecision.COMBINED

    # 4. Fetch Wikipedia if needed
    wiki_passages: list[WikiPassage] = []
    if decision in (SourceDecision.WIKIPEDIA, SourceDecision.COMBINED):
        wiki_passages = search_wikipedia(query, top_k=config.wiki_top_k)

    # 5. Build context from decided sources
    context_parts: list[str] = []

    if decision in (SourceDecision.LOCAL, SourceDecision.COMBINED):
        # Use CORRECT + AMBIGUOUS chunks
        good_chunks = [
            local_chunks[g.chunk_idx]
            for g in grades
            if g.grade != RelevanceGrade.INCORRECT and g.chunk_idx < len(local_chunks)
        ]
        if not good_chunks:
            good_chunks = local_chunks  # fallback: use all
        for i, chunk in enumerate(good_chunks):
            source = chunk.metadata.get("source", "unknown")
            context_parts.append(
                f"[Local Document — {source}]\n{chunk.page_content}"
            )

    if decision in (SourceDecision.WIKIPEDIA, SourceDecision.COMBINED):
        for wp in wiki_passages:
            context_parts.append(
                f"[Wikipedia — {wp.title}]\n{wp.extract}"
            )

    context = "\n\n---\n\n".join(context_parts)

    # 6. Generate answer
    source_label = decision.value
    ans_resp = llm.invoke([
        SystemMessage(content=(
            f"You are a helpful assistant. Answer the question using the provided context. "
            f"The context comes from: {source_label}. "
            "Be factual and concise. Cite the source type (Local or Wikipedia) when relevant."
        )),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"),
    ])

    # Build source names for display
    source_names: list[str] = []
    if decision in (SourceDecision.LOCAL, SourceDecision.COMBINED):
        source_names += list(dict.fromkeys(
            c.metadata.get("source", "unknown") for c in local_chunks
        ))
    if wiki_passages:
        source_names += [f"Wikipedia: {wp.title}" for wp in wiki_passages]

    return CRAGResult(
        query=query,
        answer=ans_resp.content.strip(),
        source_decision=decision,
        chunk_grades=grades,
        local_chunks=local_chunks,
        wiki_passages=wiki_passages,
        source_names=source_names,
    )
