from app.models.schemas import SearchResult

class CrossEncoderReranker:
    """
    Stage 1: retrieve 20-100 candidates cheaply.
    Stage 2: cross-encoder scores query/document pairs more precisely.
    """

    def __init__(self, model_name: str):
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, results: list[SearchResult], top_k: int = 8):
        pairs = [(query, r.chunk.text) for r in results]
        scores = self.model.predict(pairs)
        rescored = [
            SearchResult(chunk=r.chunk, score=float(s), retrieval_method="cross_encoder")
            for r, s in zip(results, scores)
        ]
        return sorted(rescored, key=lambda x: x.score, reverse=True)[:top_k]
