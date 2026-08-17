"""
Self-RAG service for UC4.

LangGraph StateGraph:

    retrieve → generate → critique → (rewrite → retrieve → generate → critique)* → END

New capability over UC3 (Agentic RAG):
  UC3 controls retrieval quality — it decides when and how to search.
  UC4 controls generation quality — after producing an answer it scores the answer
  on three dimensions and rewrites if any score is too low.

  Three critique dimensions (each scored 1–5):
    Groundedness  — is every claim in the answer actually supported by the retrieved passages?
    Relevance     — does the answer directly address the question asked?
    Completeness  — does the answer cover all key points in the passages?

  If any dimension falls below the threshold the pipeline rewrites the query,
  re-retrieves, and regenerates — up to max_attempts times.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TypedDict

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CritiqueRecord:
    """Scores for one generation attempt."""
    attempt: int
    answer: str
    groundedness: int   # 1–5
    relevance: int      # 1–5
    completeness: int   # 1–5

    @property
    def passed(self) -> bool:
        return False  # filled in by the graph using the configured threshold

    def scores_ok(self, threshold: int) -> bool:
        return (self.groundedness >= threshold
                and self.relevance >= threshold
                and self.completeness >= threshold)

    @property
    def avg(self) -> float:
        return round((self.groundedness + self.relevance + self.completeness) / 3, 1)


@dataclass
class SelfRAGConfig:
    """Tunable parameters for Self-RAG."""
    llm_model: str = "llama-3.3-70b-versatile"
    top_k: int = 4
    temperature: float = 0.0
    max_attempts: int = 3
    critique_threshold: int = 3   # each dimension must score >= this (scale 1–5)


@dataclass
class SelfRAGResult:
    """One query–response pair with full critique history."""
    query: str
    final_answer: str
    critique_history: list[CritiqueRecord] = field(default_factory=list)
    attempts: int = 0
    source_chunks: list[Document] = field(default_factory=list)
    source_names: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class SelfRAGState(TypedDict):
    original_query: str
    current_query: str
    chunks: list            # list[Document]
    answer: str
    attempt: int
    critique_history: list  # list[dict] — serialised CritiqueRecord
    done: bool


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
# Graph builder
# ---------------------------------------------------------------------------

def build_self_rag_graph(vectorstore, llm, config: SelfRAGConfig):
    """Return a compiled LangGraph graph with vectorstore and LLM bound."""

    # ── Nodes ────────────────────────────────────────────────────────────────

    def retrieve_node(state: SelfRAGState) -> SelfRAGState:
        chunks = vectorstore.similarity_search(state["current_query"], k=config.top_k)
        return {**state, "chunks": chunks}

    def generate_node(state: SelfRAGState) -> SelfRAGState:
        chunks: list[Document] = state["chunks"]
        context = "\n\n---\n\n".join(
            f"[{i + 1}] (source: {c.metadata.get('source', 'unknown')})\n{c.page_content}"
            for i, c in enumerate(chunks)
        )
        response = llm.invoke([
            SystemMessage(content=(
                "You are a precise document assistant. "
                "Answer the question using ONLY the provided context. "
                "Be thorough and cover all key points in the context relevant to the question."
            )),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {state['original_query']}\n\nAnswer:"),
        ])
        return {**state, "answer": response.content.strip()}

    def critique_node(state: SelfRAGState) -> SelfRAGState:
        chunks: list[Document] = state["chunks"]
        context = "\n\n".join(c.page_content[:300] for c in chunks)
        answer = state["answer"]
        query = state["original_query"]

        response = llm.invoke([
            SystemMessage(content=(
                "You are a strict answer quality evaluator. "
                "Score the answer on exactly three dimensions, each from 1 to 5:\n"
                "  Groundedness: Is every claim in the answer supported by the context? "
                "(5 = fully supported, 1 = contains unsupported claims)\n"
                "  Relevance: Does the answer directly address the question? "
                "(5 = directly answers it, 1 = off-topic)\n"
                "  Completeness: Does the answer cover all key points from the context relevant to the question? "
                "(5 = nothing important missing, 1 = major gaps)\n\n"
                "Respond in exactly this format — numbers only, no extra text:\n"
                "Groundedness: <1-5>\n"
                "Relevance: <1-5>\n"
                "Completeness: <1-5>"
            )),
            HumanMessage(content=(
                f"Question: {query}\n\n"
                f"Context:\n{context}\n\n"
                f"Answer:\n{answer}"
            )),
        ])

        # Parse scores
        text = response.content.strip()
        def _parse(label: str) -> int:
            m = re.search(rf"{label}:\s*([1-5])", text, re.IGNORECASE)
            return int(m.group(1)) if m else 3

        g = _parse("Groundedness")
        r = _parse("Relevance")
        c = _parse("Completeness")

        record = {
            "attempt": state["attempt"] + 1,
            "answer": answer,
            "groundedness": g,
            "relevance": r,
            "completeness": c,
        }

        passed = (g >= config.critique_threshold
                  and r >= config.critique_threshold
                  and c >= config.critique_threshold)
        at_limit = (state["attempt"] + 1) >= config.max_attempts

        return {
            **state,
            "attempt": state["attempt"] + 1,
            "critique_history": state["critique_history"] + [record],
            "done": passed or at_limit,
        }

    def rewrite_node(state: SelfRAGState) -> SelfRAGState:
        """Reformulate the query based on the latest critique."""
        last = state["critique_history"][-1]
        weak = [d for d, s in [("groundedness", last["groundedness"]),
                                ("relevance", last["relevance"]),
                                ("completeness", last["completeness"])]
                if s < config.critique_threshold]

        response = llm.invoke([
            SystemMessage(content=(
                "You are a query improvement assistant. "
                "Rewrite the question to produce a more grounded, relevant, and complete answer. "
                "Return ONLY the rewritten question."
            )),
            HumanMessage(content=(
                f"Original question: {state['original_query']}\n"
                f"Current query: {state['current_query']}\n"
                f"Weak dimensions: {', '.join(weak)}\n\n"
                "Rewritten query:"
            )),
        ])
        return {**state, "current_query": response.content.strip()}

    # ── Routing ──────────────────────────────────────────────────────────────

    def route_after_critique(state: SelfRAGState) -> str:
        return "end" if state["done"] else "rewrite"

    # ── Assemble ─────────────────────────────────────────────────────────────

    graph = StateGraph(SelfRAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("critique", critique_node)
    graph.add_node("rewrite", rewrite_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "critique")
    graph.add_conditional_edges("critique", route_after_critique,
                                {"end": END, "rewrite": "rewrite"})
    graph.add_edge("rewrite", "retrieve")

    return graph.compile()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_self_rag_query(
    query: str,
    vectorstore,
    config: SelfRAGConfig,
) -> SelfRAGResult:
    """Run the Self-RAG graph and return a fully critiqued result.

    Args:
        query:       Natural language question from the user.
        vectorstore: Built Chroma instance.
        config:      SelfRAGConfig with model and critique parameters.

    Returns:
        SelfRAGResult with final answer, critique history, and source attribution.
    """
    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )

    graph = build_self_rag_graph(vectorstore, llm, config)

    initial_state: SelfRAGState = {
        "original_query": query,
        "current_query": query,
        "chunks": [],
        "answer": "",
        "attempt": 0,
        "critique_history": [],
        "done": False,
    }

    final_state = graph.invoke(initial_state)

    chunks: list[Document] = final_state["chunks"]
    critique_history = [
        CritiqueRecord(
            attempt=r["attempt"],
            answer=r["answer"],
            groundedness=r["groundedness"],
            relevance=r["relevance"],
            completeness=r["completeness"],
        )
        for r in final_state["critique_history"]
    ]
    seen_sources = list(dict.fromkeys(c.metadata.get("source", "unknown") for c in chunks))

    return SelfRAGResult(
        query=query,
        final_answer=final_state["answer"],
        critique_history=critique_history,
        attempts=final_state["attempt"],
        source_chunks=chunks,
        source_names=seen_sources,
    )
