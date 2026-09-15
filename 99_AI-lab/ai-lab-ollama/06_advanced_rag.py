"""
06_advanced_rag.py - Reranking + Query Expansion + Metadata Filtering
======================================================================
MUST REMEMBER:
✓ Query expansion: use LLM to generate alternatives
✓ Reranking: LLM-based scoring on top-k
✓ Metadata filtering: pre-filter before retrieval
✓ Two-stage: retrieve broad (fast), rank precise (accurate)

KEY: Query expansion, LLM reranking, metadata filtering
"""

from anthropic import Anthropic
import json

API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"


class QueryExpander:
    """Expand queries with LLM"""

    def __init__(self):
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

    def expand_query(self, query: str):
        """Generate alternative phrasings"""
        prompt = f'Generate 3 alternative phrasings of: "{query}". Return ONLY queries, one per line.'

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )

            alternatives = response.content[0].text.strip().split("\n")
            return [query] + [q.strip() for q in alternatives if q.strip()]

        except Exception as e:
            print(f"⚠️ Expansion failed: {e}")
            return [query]


class MetadataFilter:
    """Filter documents by metadata"""

    @staticmethod
    def apply_filters(documents, filters):
        """Filter by metadata criteria"""
        result = documents

        for key, value in filters.items():
            if key == "category":
                if isinstance(value, list):
                    result = [d for d in result if d.get("metadata", {}).get("category") in value]
                else:
                    result = [d for d in result if d.get("metadata", {}).get("category") == value]
            else:
                result = [d for d in result if d.get("metadata", {}).get(key) == value]

        return result


class LLMReranker:
    """Rerank documents using LLM"""

    def __init__(self):
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

    def rerank(self, query: str, documents, top_k: int = 3):
        """LLM-based reranking"""
        if not documents:
            return []

        candidates = documents[:10]

        # Create prompt
        doc_text = "\n\n".join([
            f"[{i}] {doc['content'][:200]}"
            for i, doc in enumerate(candidates)
        ])

        prompt = f'Query: "{query}"\n\nRank by relevance (return JSON array of indices): {doc_text}'

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            start = text.find("[")
            end = text.rfind("]") + 1
            ranking = json.loads(text[start:end])

            # Reorder by ranking
            ranked = []
            for rank, idx in enumerate(ranking):
                if 0 <= idx < len(candidates):
                    score = 1.0 - (rank / len(ranking))
                    ranked.append((score, candidates[idx]))

            return ranked[:top_k]

        except Exception as e:
            print(f"⚠️ Reranking failed: {e}")
            return [(1.0 - i/len(candidates), doc) for i, doc in enumerate(candidates[:top_k])]


class AdvancedRAG:
    """Complete advanced RAG pipeline"""

    def __init__(self):
        self.expander = QueryExpander()
        self.reranker = LLMReranker()

    def search(self, query, documents, metadata_filters=None, use_expansion=True, use_reranking=True):
        """Full RAG pipeline"""
        print(f"\n🔍 Query: {query}")

        # Step 1: Metadata filter
        if metadata_filters:
            documents = MetadataFilter.apply_filters(documents, metadata_filters)
            print(f"   📍 Filtered to {len(documents)} docs")

        # Step 2: Query expansion
        queries = [query]
        if use_expansion:
            queries = self.expander.expand_query(query)
            print(f"   📝 {len(queries)} expanded queries")

        # Step 3: Retrieve (simulated)
        candidates = documents[:10]
        print(f"   📦 Retrieved {len(candidates)} candidates")

        # Step 4: Rerank
        if use_reranking and candidates:
            ranked = self.reranker.rerank(query, candidates, top_k=3)
            final_docs = [doc for _, doc in ranked]
            print(f"   ⭐ Reranked to {len(final_docs)} results")
        else:
            final_docs = candidates[:3]

        return final_docs


def main():
    print("=" * 60)
    print("06: ADVANCED RAG")
    print("=" * 60)

    # Sample documents
    documents = [
        {
            "id": "1",
            "content": "Machine learning is a subset of AI",
            "metadata": {"category": "ML", "source": "textbook"}
        },
        {
            "id": "2",
            "content": "Deep learning uses multiple neural layers",
            "metadata": {"category": "DL", "source": "paper"}
        },
        {
            "id": "3",
            "content": "Neural networks inspired by biology",
            "metadata": {"category": "ML", "source": "blog"}
        },
        {
            "id": "4",
            "content": "RAG retrieves external knowledge",
            "metadata": {"category": "RAG", "source": "paper"}
        },
    ]

    rag = AdvancedRAG()

    # Example 1: Basic search
    print("\n📝 Example 1: Basic Search")
    print("-" * 40)
    results = rag.search(
        "machine learning basics",
        documents,
        use_expansion=False,
        use_reranking=False
    )
    for doc in results:
        print(f"✅ {doc['id']}: {doc['content'][:50]}...")

    # Example 2: With metadata filter
    print("\n📝 Example 2: With Metadata Filter")
    print("-" * 40)
    results = rag.search(
        "learning",
        documents,
        metadata_filters={"category": "ML"},
        use_expansion=False,
        use_reranking=False
    )
    for doc in results:
        print(f"✅ {doc['id']}: {doc['content'][:50]}...")

    # Example 3: Full pipeline
    print("\n📝 Example 3: Full Advanced Pipeline")
    print("-" * 40)
    results = rag.search(
        "neural networks",
        documents,
        metadata_filters={"category": ["ML", "DL"]},
        use_expansion=True,
        use_reranking=True
    )
    for doc in results:
        print(f"✅ {doc['id']}: {doc['content'][:50]}...")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. QUERY EXPANSION: 2-3 alternatives, combine results
2. METADATA FILTER: Cheap, reduce early
3. RERANKING: LLM-based, only top-k
4. PIPELINE: Filter → Expand → Retrieve → Rerank
5. QUALITY: Much better results with all steps
    """)


if __name__ == "__main__":
    main()
