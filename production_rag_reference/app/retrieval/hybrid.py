from collections import defaultdict
from app.models.schemas import SearchResult

def reciprocal_rank_fusion(result_lists, k: int = 60, top_k: int = 20):
    """
    RRF score = sum(1 / (k + rank)).
    Useful because dense/BM25 scores are not naturally comparable.
    """
    scores = defaultdict(float)
    representative = {}
    for results in result_lists:
        for rank, item in enumerate(results, start=1):
            key = item.chunk.id
            scores[key] += 1 / (k + rank)
            representative[key] = item

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [
        SearchResult(
            chunk=representative[key].chunk,
            score=score,
            retrieval_method="rrf",
        )
        for key, score in ranked
    ]
