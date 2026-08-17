"""
Agentic RAG service for UC3.

LangGraph StateGraph with 5 nodes:

    classify → retrieve → evaluate → (reformulate → retrieve)* → generate

New capability over UC2 (Hybrid Search):
  UC2 always retrieves exactly once with a fixed query.
  UC3 retrieves adaptively:
    - Skips retrieval entirely if the LLM can answer without documents.
    - Reformulates the query and re-retrieves if the first context is weak.
    - Stops when context quality is sufficient OR max_iterations is reached.

The agent's reasoning trace is captured at every node so the UI can show
exactly what decisions were made and why.
"""

from __future__ import annotations

import os
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
class TraceStep:
    """One step in the agent's reasoning trace."""
    node: str        # classify | retrieve | evaluate | reformulate | generate
    message: str     # short summary shown in the UI
    detail: str = "" # optional extra info (query used, score, etc.)


@dataclass
class AgentRAGConfig:
    """Tunable parameters for Agentic RAG."""
    llm_model: str = "gemma2-9b-it"
    top_k: int = 4
    temperature: float = 0.0
    max_iterations: int = 3
    context_threshold: int = 6   # context quality score (0–10) to stop iterating


@dataclass
class AgentRAGResult:
    """One query–response pair with full agent trace."""
    query: str
    answer: str
    trace: list[TraceStep] = field(default_factory=list)
    iterations: int = 0
    source_chunks: list[Document] = field(default_factory=list)
    source_names: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    original_query: str
    current_query: str
    chunks: list            # list[Document]
    context_score: int      # 0–10 quality rating
    iteration: int
    trace: list             # list[dict] — serialised TraceStep
    answer: str
    needs_retrieval: bool


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
# Graph builder (closures capture vectorstore / llm / config)
# ---------------------------------------------------------------------------

def build_agentic_rag_graph(vectorstore, llm, config: AgentRAGConfig):
    """Return a compiled LangGraph graph with vectorstore and LLM bound."""

    # --- Nodes ---------------------------------------------------------------

    def classify_node(state: AgentState) -> AgentState:
        """Decide whether documents need to be retrieved at all."""
        response = llm.invoke([
            SystemMessage(content=(
                "You are a routing assistant. "
                "Decide if answering the question requires looking up documents. "
                "Answer with YES or NO followed by a one-line reason."
            )),
            HumanMessage(content=f"Question: {state['original_query']}"),
        ])
        text = response.content.strip()
        needs = not text.upper().startswith("NO")
        trace_entry = {"node": "classify",
                       "message": f"Retrieval needed: {'Yes' if needs else 'No'}",
                       "detail": text}
        return {**state, "needs_retrieval": needs, "trace": state["trace"] + [trace_entry]}

    def retrieve_node(state: AgentState) -> AgentState:
        """Fetch top-k chunks from ChromaDB using the current query."""
        query = state["current_query"]
        chunks = vectorstore.similarity_search(query, k=config.top_k)
        iteration = state["iteration"] + 1
        trace_entry = {"node": "retrieve",
                       "message": f"Retrieved {len(chunks)} chunks",
                       "detail": f'Query: "{query}"  ·  Iteration {iteration}'}
        return {**state, "chunks": chunks, "iteration": iteration,
                "trace": state["trace"] + [trace_entry]}

    def evaluate_node(state: AgentState) -> AgentState:
        """Rate how well the retrieved chunks answer the question (0–10)."""
        context = "\n\n".join(c.page_content[:300] for c in state["chunks"])
        response = llm.invoke([
            SystemMessage(content=(
                "You are a context quality evaluator. "
                "Rate how well the context answers the question on a scale of 0–10. "
                "Respond with ONLY the number."
            )),
            HumanMessage(content=(
                f"Question: {state['original_query']}\n\n"
                f"Context:\n{context}\n\n"
                "Quality score (0–10):"
            )),
        ])
        try:
            digits = "".join(c for c in response.content.strip() if c.isdigit())
            score = max(0, min(10, int(digits[:2] if len(digits) > 1 else digits or "5")))
        except Exception:
            score = 5
        sufficient = score >= config.context_threshold or state["iteration"] >= config.max_iterations
        trace_entry = {"node": "evaluate",
                       "message": f"Context quality: {score}/10",
                       "detail": f"Threshold {config.context_threshold}/10 — {'Sufficient ✓' if sufficient else 'Too low, reformulating'}"}
        return {**state, "context_score": score, "trace": state["trace"] + [trace_entry]}

    def reformulate_node(state: AgentState) -> AgentState:
        """Rewrite the query to improve retrieval recall."""
        response = llm.invoke([
            SystemMessage(content=(
                "You are a query reformulation assistant. "
                "Rewrite the query to be more specific and keyword-rich for document retrieval. "
                "Return ONLY the reformulated query — no explanation."
            )),
            HumanMessage(content=(
                f"Original question: {state['original_query']}\n"
                f"Current query: {state['current_query']}\n\n"
                "Reformulated query:"
            )),
        ])
        new_query = response.content.strip()
        trace_entry = {"node": "reformulate",
                       "message": "Query reformulated",
                       "detail": f'"{state["current_query"]}"  →  "{new_query}"'}
        return {**state, "current_query": new_query, "trace": state["trace"] + [trace_entry]}

    def generate_node(state: AgentState) -> AgentState:
        """Generate the final answer from accumulated context."""
        chunks: list[Document] = state["chunks"]
        if chunks:
            context = "\n\n---\n\n".join(
                f"[{i + 1}] (source: {c.metadata.get('source', 'unknown')})\n{c.page_content}"
                for i, c in enumerate(chunks)
            )
            system = (
                "You are a precise document assistant. "
                "Answer the question using ONLY the provided context. "
                "If the answer is not in the context, say so clearly."
            )
            user_msg = f"Context:\n{context}\n\nQuestion: {state['original_query']}\n\nAnswer:"
        else:
            system = "You are a helpful assistant. Answer the question directly and concisely."
            user_msg = f"Question: {state['original_query']}"

        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
        n_docs = len(set(c.metadata.get("source", "") for c in chunks))
        trace_entry = {"node": "generate",
                       "message": "Answer generated",
                       "detail": f"{len(chunks)} chunks from {n_docs} document(s)" if chunks else "No retrieval used"}
        return {**state, "answer": response.content.strip(), "trace": state["trace"] + [trace_entry]}

    # --- Conditional routing --------------------------------------------------

    def route_classify(state: AgentState) -> str:
        return "retrieve" if state["needs_retrieval"] else "generate"

    def route_evaluate(state: AgentState) -> str:
        if state["context_score"] >= config.context_threshold:
            return "generate"
        if state["iteration"] >= config.max_iterations:
            return "generate"
        return "reformulate"

    # --- Assemble graph -------------------------------------------------------

    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("reformulate", reformulate_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("classify")
    graph.add_conditional_edges("classify", route_classify,
                                {"retrieve": "retrieve", "generate": "generate"})
    graph.add_edge("retrieve", "evaluate")
    graph.add_conditional_edges("evaluate", route_evaluate,
                                {"generate": "generate", "reformulate": "reformulate"})
    graph.add_edge("reformulate", "retrieve")
    graph.add_edge("generate", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_agentic_rag_query(
    query: str,
    vectorstore,
    config: AgentRAGConfig,
) -> AgentRAGResult:
    """Run the agentic RAG graph and return a fully attributed result.

    Args:
        query:       Natural language question from the user.
        vectorstore: Built Chroma instance (from vector_store.build_vector_store).
        config:      AgentRAGConfig with model and agent parameters.

    Returns:
        AgentRAGResult with answer, trace, source chunks, and iteration count.
    """
    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )

    graph = build_agentic_rag_graph(vectorstore, llm, config)

    initial_state: AgentState = {
        "original_query": query,
        "current_query": query,
        "chunks": [],
        "context_score": 0,
        "iteration": 0,
        "trace": [],
        "answer": "",
        "needs_retrieval": True,
    }

    final_state = graph.invoke(initial_state)

    chunks: list[Document] = final_state["chunks"]
    trace = [
        TraceStep(node=t["node"], message=t["message"], detail=t.get("detail", ""))
        for t in final_state["trace"]
    ]
    seen_sources = list(dict.fromkeys(c.metadata.get("source", "unknown") for c in chunks))

    return AgentRAGResult(
        query=query,
        answer=final_state["answer"],
        trace=trace,
        iterations=final_state["iteration"],
        source_chunks=chunks,
        source_names=seen_sources,
    )
