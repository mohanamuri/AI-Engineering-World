from rank_bm25 import BM25Okapi
from app.models.schemas import SearchResult

class BM25Retriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.index = BM25Okapi([c.text.lower().split() for c in chunks])

    def search(self, query: str, top_k: int = 20):
        scores = self.index.get_scores(query.lower().split())
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            SearchResult(chunk=self.chunks[i], score=float(score), retrieval_method="bm25")
            for i, score in ranked
        ]
