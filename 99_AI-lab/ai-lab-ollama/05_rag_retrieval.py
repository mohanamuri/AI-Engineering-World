"""
05_rag_retrieval.py - Dense + Sparse + Hybrid Search
====================================================
MUST REMEMBER:
✓ Dense: good for semantic, bad for rare words
✓ Sparse (BM25): good for keywords
✓ Hybrid: combines both strengths
✓ Always retrieve more than needed, then re-rank

KEY: Dense retrieval, BM25, hybrid scoring
"""

import math
from typing import List, Dict, Tuple
from collections import defaultdict


class DenseRetriever:
    """Dense retrieval using cosine similarity"""

    def __init__(self, chunks: List[Dict]):
        self.chunks = chunks

    def _embed_text(self, text: str) -> List[float]:
        """Simple embedding"""
        v = [0.0] * 10
        for i, c in enumerate(text):
            v[i % 10] += ord(c)
        mag = math.sqrt(sum(x**2 for x in v))
        return [x / mag for x in v] if mag > 0 else v

    def _cosine_sim(self, a: List[float], b: List[float]) -> float:
        """Cosine similarity"""
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x**2 for x in a))
        mag_b = math.sqrt(sum(x**2 for x in b))
        return dot / (mag_a * mag_b) if mag_a > 0 and mag_b > 0 else 0

    def search(self, query: str, k: int = 3) -> List[Tuple[float, Dict]]:
        """Dense search"""
        query_emb = self._embed_text(query)
        scores = []

        for chunk in self.chunks:
            chunk_emb = self._embed_text(chunk["content"])
            sim = self._cosine_sim(query_emb, chunk_emb)
            scores.append((sim, chunk))

        return sorted(scores, reverse=True)[:k]


class BM25Retriever:
    """BM25 keyword search"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs = []
        self.idf = {}

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def index(self, documents: List[Dict]) -> None:
        """Build BM25 index"""
        self.docs = documents
        doc_count = len(documents)
        word_doc_count = defaultdict(int)

        for doc in documents:
            tokens = set(self._tokenize(doc["content"]))
            for token in tokens:
                word_doc_count[token] += 1

        for word, count in word_doc_count.items():
            self.idf[word] = math.log((doc_count - count + 0.5) / (count + 0.5) + 1)

    def search(self, query: str, k: int = 3) -> List[Tuple[float, Dict]]:
        """BM25 search"""
        query_tokens = self._tokenize(query)
        scores = defaultdict(float)

        avg_len = sum(len(self._tokenize(d["content"])) for d in self.docs) / len(self.docs)

        for doc_idx, doc in enumerate(self.docs):
            doc_tokens = self._tokenize(doc["content"])
            doc_len = len(doc_tokens)
            token_counts = defaultdict(int)

            for token in doc_tokens:
                token_counts[token] += 1

            for qt in query_tokens:
                if qt not in token_counts:
                    continue
                tf = token_counts[qt]
                idf = self.idf.get(qt, 0)
                score = idf * ((tf * (self.k1 + 1)) /
                               (tf + self.k1 * (1 - self.b + self.b * (doc_len / avg_len))))
                scores[doc_idx] += score

        ranked = sorted([(scores[idx], self.docs[idx]) for idx in scores], reverse=True)
        return ranked[:k]


class HybridRetriever:
    """Combine dense and sparse retrieval"""

    def __init__(self, dense_weight: float = 0.6, sparse_weight: float = 0.4):
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

    def initialize(self, chunks: List[Dict]) -> None:
        self.dense = DenseRetriever(chunks)
        self.bm25 = BM25Retriever()
        self.bm25.index(chunks)

    def search(self, query: str, k: int = 3) -> List[Tuple[float, Dict]]:
        """Hybrid search"""
        dense_results = self.dense.search(query, k * 2)
        sparse_results = self.bm25.search(query, k * 2)

        combined = {}

        # Normalize and combine
        max_d = dense_results[0][0] if dense_results else 1.0
        for score, chunk in dense_results:
            normalized = (score / max_d if max_d > 0 else 0) * self.dense_weight
            combined.setdefault(chunk["id"], 0)
            combined[chunk["id"]] += normalized

        max_s = sparse_results[0][0] if sparse_results else 1.0
        for score, chunk in sparse_results:
            normalized = (score / max_s if max_s > 0 else 0) * self.sparse_weight
            combined.setdefault(chunk["id"], 0)
            combined[chunk["id"]] += normalized

        # Return top-k
        chunks_by_id = {c["id"]: c for c in (dense_results + sparse_results) if c}
        ranked = sorted(
            [(score, chunks_by_id.get(cid)) for cid, score in combined.items()],
            reverse=True
        )[:k]

        return [(s, c) for s, c in ranked if c]


def main():
    print("=" * 60)
    print("05: RAG RETRIEVAL (Dense + Sparse + Hybrid)")
    print("=" * 60)

    chunks = [
        {"id": "1", "content": "Machine learning is AI subset"},
        {"id": "2", "content": "Neural networks deep learning"},
        {"id": "3", "content": "Deep learning multiple layers"},
        {"id": "4", "content": "RAG retrieves external knowledge"},
        {"id": "5", "content": "Embeddings convert text vectors"},
    ]

    # Test each method
    print("\n📝 Example 1: BM25 (Keyword)")
    print("-" * 40)
    bm25 = BM25Retriever()
    bm25.index(chunks)
    results = bm25.search("neural networks", k=2)
    for score, chunk in results:
        print(f"✅ {chunk['id']}: {chunk['content']} ({score:.2f})")

    print("\n📝 Example 2: Dense (Semantic)")
    print("-" * 40)
    dense = DenseRetriever(chunks)
    results = dense.search("deep learning", k=2)
    for score, chunk in results:
        print(f"✅ {chunk['id']}: {chunk['content']} ({score:.2f})")

    print("\n📝 Example 3: Hybrid (Combined)")
    print("-" * 40)
    hybrid = HybridRetriever()
    hybrid.initialize(chunks)
    results = hybrid.search("machine learning networks", k=3)
    for score, chunk in results:
        print(f"✅ {chunk['id']}: {chunk['content']} ({score:.2f})")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. DENSE: Fast, semantic, bad for rare words
2. BM25: Slow, keywords, good for exact matches
3. HYBRID: Retrieve broad, rank precise (best quality)
4. NORMALIZE: Before combining scores
5. RETRIEVE: More than needed, then rank
    """)


if __name__ == "__main__":
    main()
