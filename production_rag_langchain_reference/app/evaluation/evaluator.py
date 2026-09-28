"""
Evaluation and continuous monitoring.

Tracks RAG quality using:
- Golden dataset: hand-annotated Q&A pairs with expected citations
- RAGAS metrics: retrieval-augmented generation assessment
- Human feedback: user thumbs-up/down on answers
"""

from pydantic import BaseModel


class GoldenExample(BaseModel):
    """Hand-annotated golden example for evaluation."""
    question: str
    expected_answer: str
    expected_source_ids: list[str]


class EvaluationMetrics(BaseModel):
    """Metrics from evaluating a RAG response."""
    retrieval_precision: float  # % of retrieved docs that are relevant
    retrieval_recall: float  # % of relevant docs that were retrieved
    answer_correctness: float  # 0-1 score of answer accuracy
    citation_precision: float  # % of cited sources that are relevant


def load_golden_set(path: str = "app/evaluation/golden_set.json") -> list[GoldenExample]:
    """
    Load golden evaluation set from JSON.

    Args:
        path: Path to golden_set.json

    Returns:
        List of GoldenExample objects
    """
    import json
    with open(path) as f:
        data = json.load(f)
    return [GoldenExample(**item) for item in data]


def evaluate_retrieval(retrieved_ids: list[str], expected_ids: list[str]) -> dict:
    """
    Compute retrieval metrics.

    Args:
        retrieved_ids: IDs of retrieved documents
        expected_ids: IDs of relevant documents

    Returns:
        Dict with precision, recall scores
    """
    retrieved_set = set(retrieved_ids)
    expected_set = set(expected_ids)

    true_positives = len(retrieved_set & expected_set)
    false_positives = len(retrieved_set - expected_set)
    false_negatives = len(expected_set - retrieved_set)

    precision = true_positives / len(retrieved_set) if retrieved_set else 0.0
    recall = true_positives / len(expected_set) if expected_set else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0,
    }
