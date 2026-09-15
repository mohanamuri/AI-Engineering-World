"""
07_rag_evaluation.py - Retrieval Quality Metrics
================================================
MUST REMEMBER:
✓ Precision@k: |relevant in top-k| / k
✓ Recall@k: |relevant in top-k| / total_relevant
✓ NDCG@k: ranking quality (0-1)
✓ MRR: reciprocal rank of first relevant
✓ MAP: mean average precision

KEY: Multiple metrics, evaluation dataset, quality tracking
"""

from typing import List, Dict


class RetrievalMetrics:
    """Calculate retrieval quality metrics"""

    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: List[str], k: int = 3) -> float:
        """Precision@k = |relevant in top-k| / k"""
        if k == 0:
            return 0.0
        hits = sum(1 for doc_id in retrieved[:k] if doc_id in relevant)
        return hits / k

    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: List[str], k: int = 3) -> float:
        """Recall@k = |relevant in top-k| / |all relevant|"""
        if not relevant:
            return 0.0
        hits = sum(1 for doc_id in retrieved[:k] if doc_id in relevant)
        return hits / len(relevant)

    @staticmethod
    def dcg_at_k(retrieved: List, relevant: List[str], k: int = 3) -> float:
        """DCG = sum of relevance / log(position)"""
        dcg = 0.0
        for i, item in enumerate(retrieved[:k]):
            doc_id = item if isinstance(item, str) else item["id"]
            if doc_id in relevant:
                dcg += 1.0 / (i + 1)
        return dcg

    @staticmethod
    def ndcg_at_k(retrieved: List, relevant: List[str], k: int = 3) -> float:
        """NDCG = DCG / IDCG (normalized 0-1)"""
        dcg = RetrievalMetrics.dcg_at_k(retrieved, relevant, k)
        ideal = RetrievalMetrics.dcg_at_k(relevant, relevant, k)
        return dcg / ideal if ideal > 0 else 0.0

    @staticmethod
    def mrr(retrieved: List[str], relevant: List[str]) -> float:
        """MRR = 1 / rank of first relevant"""
        for rank, doc_id in enumerate(retrieved, 1):
            if doc_id in relevant:
                return 1.0 / rank
        return 0.0

    @staticmethod
    def map_score(retrieved: List[str], relevant: List[str], k: int = 10) -> float:
        """MAP = sum of precisions / total_relevant"""
        if not relevant:
            return 0.0
        score = 0.0
        hits = 0
        for i, doc_id in enumerate(retrieved[:k]):
            if doc_id in relevant:
                hits += 1
                score += hits / (i + 1)
        return score / len(relevant)


class RAGEvaluator:
    """Evaluate RAG system quality"""

    def __init__(self):
        self.results = []

    def evaluate_query(self, query: str, retrieved: List[str], relevant: List[str]) -> Dict:
        """Evaluate single query"""
        metrics = {
            "query": query,
            "precision@3": RetrievalMetrics.precision_at_k(retrieved, relevant, k=3),
            "recall@3": RetrievalMetrics.recall_at_k(retrieved, relevant, k=3),
            "ndcg@3": RetrievalMetrics.ndcg_at_k(retrieved, relevant, k=3),
            "mrr": RetrievalMetrics.mrr(retrieved, relevant),
            "map": RetrievalMetrics.map_score(retrieved, relevant)
        }
        self.results.append(metrics)
        return metrics

    def get_summary(self) -> Dict:
        """Average metrics across queries"""
        if not self.results:
            return {}

        keys = ["precision@3", "recall@3", "ndcg@3", "mrr", "map"]
        summary = {}

        for key in keys:
            values = [r[key] for r in self.results]
            summary[f"{key}_avg"] = sum(values) / len(values)
            summary[f"{key}_min"] = min(values)
            summary[f"{key}_max"] = max(values)

        summary["total_queries"] = len(self.results)
        return summary


def main():
    print("=" * 60)
    print("07: RAG EVALUATION")
    print("=" * 60)

    # Test data
    test_queries = [
        {
            "query": "What is ML?",
            "retrieved": ["1", "4", "2"],
            "relevant": ["1"]
        },
        {
            "query": "Neural networks",
            "retrieved": ["2", "3", "1"],
            "relevant": ["2", "3"]
        },
        {
            "query": "How RAG works?",
            "retrieved": ["5", "4", "1"],
            "relevant": ["4"]
        }
    ]

    evaluator = RAGEvaluator()

    print("\n📊 Evaluating Queries")
    print("-" * 40)

    for test in test_queries:
        metrics = evaluator.evaluate_query(
            test["query"],
            test["retrieved"],
            test["relevant"]
        )

        print(f"\n🔍 {test['query']}")
        print(f"   Precision@3: {metrics['precision@3']:.2f}")
        print(f"   Recall@3: {metrics['recall@3']:.2f}")
        print(f"   NDCG@3: {metrics['ndcg@3']:.2f}")
        print(f"   MRR: {metrics['mrr']:.2f}")
        print(f"   MAP: {metrics['map']:.2f}")

    print("\n📈 Summary")
    print("-" * 40)
    summary = evaluator.get_summary()

    for key in ["precision@3_avg", "recall@3_avg", "ndcg@3_avg", "mrr_avg", "map_avg"]:
        print(f"✅ {key}: {summary[key]:.3f}")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. PRECISION: False positives (minimize)
2. RECALL: False negatives (find all)
3. NDCG: Ranking quality
4. MRR: Position of first answer
5. MAP: Overall system quality
6. PROCESS: Label 50+ test queries, track metrics, improve, re-evaluate
    """)


if __name__ == "__main__":
    main()
