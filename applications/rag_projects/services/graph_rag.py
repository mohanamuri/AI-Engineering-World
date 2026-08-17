"""
GraphRAG service for UC5.

How it is different from UC1–UC4:
  UC1–UC4 find chunks that are *semantically similar* to the query.
  GraphRAG finds chunks by following *entity relationships* — so it can
  discover connected information that has low surface similarity to the query.

Pipeline:
  1. After uploading documents, user clicks "Build Knowledge Graph".
  2. LLM reads each chunk and extracts (entity, relation, entity) triples.
  3. Entities become graph nodes; relations become directed edges.
     Each node stores the chunk indices where it appears.
  4. At query time:
       a. LLM extracts key entities from the question.
       b. Matching nodes are found in the graph.
       c. BFS expands outward up to max_hops to discover related entities.
       d. All chunks associated with visited entities are gathered.
       e. LLM generates an answer from those chunks.
"""

from __future__ import annotations

import os
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class GraphRAGConfig:
    """Tunable parameters for GraphRAG."""
    llm_model: str = "openai/gpt-oss-20b"
    top_k: int = 5
    temperature: float = 0.0
    max_hops: int = 2
    max_chunks_for_graph: int = 30  # limit LLM calls during graph build


@dataclass
class KnowledgeGraph:
    """In-memory knowledge graph built from document chunks."""
    # entity (str) → list of {target, relation, chunk_idx}
    edges: dict = field(default_factory=lambda: defaultdict(list))
    # entity (str) → set of chunk indices that mention it
    entity_chunks: dict = field(default_factory=lambda: defaultdict(set))
    all_entities: list = field(default_factory=list)
    edge_count: int = 0
    chunks: list = field(default_factory=list)


@dataclass
class GraphRAGResult:
    """One query–response with graph traversal details."""
    query: str
    answer: str
    matched_entities: list = field(default_factory=list)
    expanded_entities: list = field(default_factory=list)
    retrieved_chunks: list = field(default_factory=list)
    subgraph_edges: list = field(default_factory=list)
    source_names: list = field(default_factory=list)
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


def _get_llm(config: GraphRAGConfig) -> ChatGroq:
    return ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def extract_triples_from_chunk(chunk_text: str, llm: ChatGroq) -> list[tuple[str, str, str]]:
    """Use LLM to extract (entity1, relation, entity2) triples from one chunk."""
    response = llm.invoke([
        SystemMessage(content=(
            "You are an entity and relationship extraction assistant.\n"
            "Read the text and extract key entities and how they relate to each other.\n"
            "Output ONLY triples in this exact format, one per line:\n"
            "ENTITY1 | RELATION | ENTITY2\n\n"
            "Rules:\n"
            "- Entity names: 1-4 words, lowercase, specific (e.g. 'remote work policy', 'john smith')\n"
            "- Relations: short verb phrase (e.g. 'requires', 'reports_to', 'includes', 'governs')\n"
            "- Extract 3-6 meaningful triples only — skip obvious or trivial ones\n"
            "- No bullet points, no numbering, no explanation — triples only"
        )),
        HumanMessage(content=f"Text:\n{chunk_text[:900]}\n\nTriples:"),
    ])

    triples: list[tuple[str, str, str]] = []
    for line in response.content.strip().split("\n"):
        parts = [p.strip().lower() for p in line.split("|")]
        if len(parts) == 3 and all(p for p in parts):
            e1, rel, e2 = parts
            if len(e1) < 80 and len(e2) < 80 and len(rel) < 50:
                triples.append((e1, rel, e2))
    return triples


def build_knowledge_graph(
    chunks: list[Document],
    config: GraphRAGConfig,
    progress_cb=None,
) -> KnowledgeGraph:
    """Build the knowledge graph by running entity extraction over all chunks.

    Args:
        chunks:      LangChain Documents to process.
        config:      GraphRAGConfig with model settings and chunk limit.
        progress_cb: Optional callable(done, total) for Streamlit progress bars.

    Returns:
        KnowledgeGraph with edges, entity_chunks, and a reference to the chunks list.
    """
    llm = _get_llm(config)
    graph = KnowledgeGraph(chunks=chunks)

    process_chunks = chunks[:config.max_chunks_for_graph]
    total = len(process_chunks)

    for idx, chunk in enumerate(process_chunks):
        triples = extract_triples_from_chunk(chunk.page_content, llm)
        for e1, rel, e2 in triples:
            graph.edges[e1].append({"target": e2, "relation": rel, "chunk_idx": idx})
            graph.edges[e2].append({"target": e1, "relation": f"inv_{rel}", "chunk_idx": idx})
            graph.entity_chunks[e1].add(idx)
            graph.entity_chunks[e2].add(idx)
        if progress_cb:
            progress_cb(idx + 1, total)
        # Stay under Groq free-tier TPM limit (8000 tokens/min)
        time.sleep(2.5)

    graph.all_entities = sorted(graph.entity_chunks.keys())
    graph.edge_count = sum(
        1 for edges in graph.edges.values()
        for e in edges if not e["relation"].startswith("inv_")
    )
    return graph


# ---------------------------------------------------------------------------
# Graph querying
# ---------------------------------------------------------------------------

def run_graph_rag_query(
    query: str,
    graph: KnowledgeGraph,
    config: GraphRAGConfig,
) -> GraphRAGResult:
    """Query the knowledge graph.

    Steps:
      1. Extract key entities from the query using LLM.
      2. Match them to nodes in the graph (substring match).
      3. BFS-expand up to max_hops to find related entities.
      4. Gather all chunks associated with visited entities.
      5. Generate answer from those chunks.

    Args:
        query:  Natural language question.
        graph:  Pre-built KnowledgeGraph.
        config: GraphRAGConfig.

    Returns:
        GraphRAGResult with answer, matched entities, traversal path, and sources.
    """
    llm = _get_llm(config)

    # Step 1 — extract query entities
    ent_resp = llm.invoke([
        SystemMessage(content=(
            "Extract the 2-5 most important entity names from the question. "
            "Use lowercase. Output only the entities, one per line — no other text."
        )),
        HumanMessage(content=f"Question: {query}"),
    ])
    query_entities = [
        e.strip().lower()
        for e in ent_resp.content.strip().split("\n")
        if e.strip()
    ]

    # Step 2 — match to graph nodes
    matched: list[str] = []
    for qe in query_entities:
        qe_words = set(qe.split())
        for ge in graph.all_entities:
            ge_words = set(ge.split())
            if qe_words & ge_words or qe in ge or ge in qe:
                if ge not in matched:
                    matched.append(ge)

    # Fallback: keyword search if no entity match
    if not matched:
        query_lower = query.lower()
        for ge in graph.all_entities:
            if any(w in query_lower for w in ge.split() if len(w) > 3):
                if ge not in matched:
                    matched.append(ge)

    # Step 3 — BFS expansion
    visited: set[str] = set(matched)
    frontier = list(matched)
    subgraph_edges: list[tuple] = []

    for _ in range(config.max_hops):
        next_frontier: list[str] = []
        for entity in frontier:
            for edge in graph.edges.get(entity, []):
                rel = edge["relation"]
                target = edge["target"]
                if not rel.startswith("inv_"):
                    subgraph_edges.append((entity, rel, target))
                if target not in visited:
                    visited.add(target)
                    next_frontier.append(target)
        frontier = next_frontier
        if not frontier:
            break

    # Step 4 — gather chunks
    chunk_indices: set[int] = set()
    for entity in visited:
        chunk_indices.update(graph.entity_chunks.get(entity, set()))

    retrieved = [
        graph.chunks[i]
        for i in sorted(chunk_indices)
        if i < len(graph.chunks)
    ][:config.top_k]

    # Fallback — if graph found nothing, use first top_k chunks
    if not retrieved:
        retrieved = graph.chunks[: config.top_k]

    # Step 5 — generate answer
    context = "\n\n---\n\n".join(
        f"[{i + 1}] (source: {c.metadata.get('source', 'unknown')})\n{c.page_content}"
        for i, c in enumerate(retrieved)
    )
    ans_resp = llm.invoke([
        SystemMessage(content=(
            "You are a precise document assistant. "
            "Answer the question using ONLY the provided context passages. "
            "Be clear and concise. If context is insufficient, say so."
        )),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"),
    ])

    source_names = list(dict.fromkeys(
        c.metadata.get("source", "unknown") for c in retrieved
    ))

    return GraphRAGResult(
        query=query,
        answer=ans_resp.content.strip(),
        matched_entities=matched,
        expanded_entities=list(visited - set(matched)),
        retrieved_chunks=retrieved,
        subgraph_edges=subgraph_edges[:25],
        source_names=source_names,
    )


# ---------------------------------------------------------------------------
# Graph visualisation helper
# ---------------------------------------------------------------------------

def graph_to_dot(graph: KnowledgeGraph, highlight_entities: list[str] | None = None) -> str:
    """Convert a KnowledgeGraph (or subgraph) to Graphviz DOT notation.

    Args:
        graph:              The full knowledge graph.
        highlight_entities: Entities to colour differently (query matches).

    Returns:
        DOT string suitable for st.graphviz_chart().
    """
    highlight = set(highlight_entities or [])
    seen_edges: set[tuple] = set()

    lines = [
        'digraph KG {',
        '    rankdir=LR',
        '    node [shape=box style=filled fontname="Arial" fontsize=10]',
        '    edge [fontsize=9]',
    ]

    # Top entities by chunk frequency
    top_entities = sorted(
        graph.entity_chunks.keys(),
        key=lambda e: len(graph.entity_chunks[e]),
        reverse=True,
    )[:20]

    for entity in top_entities:
        label = entity.replace('"', "'")
        if entity in highlight:
            color = 'fillcolor="#fce7f3" color="#ec4899"'
        else:
            color = 'fillcolor="#dbeafe" color="#3b82f6"'
        lines.append(f'    "{label}" [{color}]')

    top_set = set(top_entities)
    for entity in top_entities:
        for edge in graph.edges.get(entity, []):
            target = edge["target"]
            rel = edge["relation"]
            if rel.startswith("inv_") or target not in top_set:
                continue
            edge_key = (entity, target)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            rel_label = rel.replace('"', "'")
            e_label = entity.replace('"', "'")
            t_label = target.replace('"', "'")
            lines.append(f'    "{e_label}" -> "{t_label}" [label="{rel_label}"]')

    lines.append("}")
    return "\n".join(lines)
