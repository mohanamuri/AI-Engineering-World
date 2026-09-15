"""
04_rag_ingestion.py - Document Loading, Chunking, Embeddings
=============================================================
MUST REMEMBER:
✓ Chunk size: 300-800 tokens (experiment)
✓ Overlap: 20-30% prevents boundary loss
✓ Metadata: preserve per chunk
✓ Consistent embedding model

KEY: Chunking strategy, embeddings, metadata preservation
"""

import math
from typing import List, Dict


class DocumentChunker:
    """Split documents into chunks with overlap"""

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        return text.split()

    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """Break documents into chunks with metadata"""
        chunks = []

        for doc in documents:
            tokens = self._tokenize(doc["content"])

            # MUST REMEMBER: Split with overlap
            for i in range(0, len(tokens), self.chunk_size - self.overlap):
                chunk_tokens = tokens[i : i + self.chunk_size]
                if not chunk_tokens:
                    continue

                chunk = {
                    "id": f"{doc.get('id', 'unknown')}_{len(chunks)}",
                    "content": " ".join(chunk_tokens),
                    "token_count": len(chunk_tokens),
                    "metadata": {**doc.get("metadata", {}), "chunk_idx": len(chunks)}
                }
                chunks.append(chunk)

        return chunks


class SimpleEmbedding:
    """Fake embeddings for demo (use real API in production)"""

    @staticmethod
    def embed_text(text: str) -> List[float]:
        """Create fake embedding vector"""
        vector = [0.0] * 10
        for i, char in enumerate(text):
            vector[i % 10] += ord(char)
        mag = math.sqrt(sum(v**2 for v in vector))
        return [v / mag for v in vector] if mag > 0 else vector


class InMemoryVectorDB:
    """Simple in-memory vector database"""

    def __init__(self):
        self.store = []

    def add_chunks(self, chunks: List[Dict]) -> None:
        """Index chunks with embeddings"""
        for chunk in chunks:
            embedding = SimpleEmbedding.embed_text(chunk["content"])
            self.store.append({
                "id": chunk["id"],
                "embedding": embedding,
                "content": chunk["content"],
                "metadata": chunk["metadata"]
            })
            print(f"✅ Indexed: {chunk['id']}")

    def similarity_search(self, query: str, k: int = 3) -> List[Dict]:
        """Find most similar chunks"""
        query_emb = SimpleEmbedding.embed_text(query)
        scores = []

        for item in self.store:
            score = sum(a * b for a, b in zip(query_emb, item["embedding"]))
            scores.append((score, item))

        return [item for _, item in sorted(scores, reverse=True)[:k]]


def main():
    print("=" * 60)
    print("04: RAG INGESTION")
    print("=" * 60)

    # Create documents
    documents = [
        {
            "id": "doc1",
            "content": "Machine learning is a subset of artificial intelligence that enables systems to learn from data. Neural networks are inspired by biological neurons.",
            "metadata": {"title": "ML Basics", "author": "AI Lab"}
        },
        {
            "id": "doc2",
            "content": "RAG combines LLMs with external knowledge retrieval. This approach improves accuracy and reduces hallucination.",
            "metadata": {"title": "RAG Systems", "author": "AI Lab"}
        }
    ]

    # Step 1: Chunk documents
    print("\n📝 Step 1: Chunk Documents")
    print("-" * 40)
    chunker = DocumentChunker(chunk_size=50, overlap=10)
    chunks = chunker.chunk_documents(documents)
    print(f"✅ Created {len(chunks)} chunks")

    # Step 2: Index with embeddings
    print("\n📝 Step 2: Create Embeddings & Index")
    print("-" * 40)
    db = InMemoryVectorDB()
    db.add_chunks(chunks)

    # Step 3: Retrieval test
    print("\n📝 Step 3: Retrieval Test")
    print("-" * 40)
    queries = ["machine learning", "RAG systems"]
    for query in queries:
        results = db.similarity_search(query, k=2)
        print(f"\n🔍 Query: {query}")
        for r in results:
            print(f"   ✅ {r['id']}: {r['content'][:50]}...")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. CHUNKING: Size 300-800 tokens, 20-30% overlap
2. METADATA: Preserve doc info in each chunk
3. EMBEDDINGS: Use consistent model (real: API-based)
4. VECTOR DB: Pinecone, Weaviate, Milvus in production
5. DEDUP: Check for duplicate documents
    """)


if __name__ == "__main__":
    main()
