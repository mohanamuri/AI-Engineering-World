"""
Hybrid retriever — BM25 + dense vector search with Reciprocal Rank Fusion.

Why hybrid?
-----------
Dense vector search finds semantically similar chunks — great for
conceptual questions ("explain the parental leave policy"). But it
compresses exact strings poorly. A chunk containing "23,000" or
"401(k)" may not rank highly by cosine similarity even though those
exact tokens directly answer the query.

BM25 is a classic TF-IDF-inspired keyword scorer that ranks chunks
by exact token overlap. It excels where dense search fails: specific
numbers, product codes, names, and technical jargon.

Reciprocal Rank Fusion (RRF) merges both ranked lists without needing
their scores to be on the same scale. A chunk ranked #1 by dense and
#3 by BM25 scores higher than one only in one list — capturing the
best of both retrievers.

RRF formula: score(d) = Σ 1/(rank_i(d) + k)  where k=60 dampens
the impact of very high ranks, preventing a single #1 result from
dominating.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.documents import Document


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class HybridResult:
    """One chunk from the fused result set with full retriever attribution."""
    doc: Document
    rrf_score: float
    dense_rank: int | None      # 1-based rank in dense results, None if absent
    bm25_rank: int | None       # 1-based rank in BM25 results, None if absent
    retriever: str              # "dense" | "bm25" | "both"


# ---------------------------------------------------------------------------
# BM25 Retriever
# ---------------------------------------------------------------------------

class BM25Retriever:
    """Lightweight BM25 index over a list of LangChain Documents.

    Built from the same chunks as the ChromaDB vector store so both
    retrievers operate on identical text units.
    """

    def __init__(self, chunks: list[Document]) -> None:
        from rank_bm25 import BM25Okapi  # deferred: only when BM25 is used

        self._chunks = chunks
        tokenized = [doc.page_content.lower().split() for doc in chunks]
        self._index = BM25Okapi(tokenized)

    def get_top_k(self, query: str, k: int = 8) -> list[tuple[Document, float]]:
        """Return top-k chunks ranked by BM25 score.

        Args:
            query: Natural language question.
            k:     Number of results to return.

        Returns:
            List of (Document, score) tuples, highest score first.
        """
        tokens = query.lower().split()
        scores = self._index.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(self._chunks[i], float(scores[i])) for i in top_indices]


# ---------------------------------------------------------------------------
# Hybrid search (RRF fusion)
# ---------------------------------------------------------------------------

def hybrid_search(
    query: str,
    vectorstore,
    bm25_retriever: BM25Retriever,
    top_k: int = 4,
    rrf_k: int = 60,
) -> list[HybridResult]:
    """Run dense + BM25 retrieval and fuse results with RRF.

    Both retrievers fetch 2×top_k candidates so the fusion has a large
    enough pool to promote chunks that appear in both lists.

    Args:
        query:          User question.
        vectorstore:    Built Chroma instance.
        bm25_retriever: BM25Retriever built from the same chunks.
        top_k:          Number of fused results to return.
        rrf_k:          RRF damping constant (default 60, per the original paper).

    Returns:
        List of HybridResult sorted by descending RRF score.
    """
    candidates = top_k * 2

    # Dense retrieval
    dense_docs: list[Document] = vectorstore.similarity_search(query, k=candidates)

    # BM25 retrieval
    bm25_docs: list[tuple[Document, float]] = bm25_retriever.get_top_k(query, k=candidates)

    # Build content-keyed maps (page_content is the stable identifier)
    rrf_scores: dict[str, float] = {}
    dense_ranks: dict[str, int] = {}
    bm25_ranks: dict[str, int] = {}
    doc_registry: dict[str, Document] = {}

    for rank, doc in enumerate(dense_docs):
        key = doc.page_content
        rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (rank + 1 + rrf_k)
        dense_ranks[key] = rank + 1
        doc_registry[key] = doc

    for rank, (doc, _) in enumerate(bm25_docs):
        key = doc.page_content
        rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (rank + 1 + rrf_k)
        bm25_ranks[key] = rank + 1
        if key not in doc_registry:
            doc_registry[key] = doc

    # Sort by RRF score, take top_k
    sorted_keys = sorted(rrf_scores, key=lambda k: rrf_scores[k], reverse=True)[:top_k]

    results: list[HybridResult] = []
    for key in sorted_keys:
        dr = dense_ranks.get(key)
        br = bm25_ranks.get(key)
        if dr and br:
            retriever = "both"
        elif dr:
            retriever = "dense"
        else:
            retriever = "bm25"

        results.append(HybridResult(
            doc=doc_registry[key],
            rrf_score=rrf_scores[key],
            dense_rank=dr,
            bm25_rank=br,
            retriever=retriever,
        ))

    return results
