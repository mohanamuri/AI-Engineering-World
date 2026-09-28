"""
Evaluation tests.

Tests for RAG quality metrics and golden set evaluation.
"""

import pytest
from app.evaluation.evaluator import evaluate_retrieval


def test_evaluate_retrieval_perfect_recall():
    """Perfect match should have precision=1.0, recall=1.0."""
    retrieved = ["doc1", "doc2", "doc3"]
    expected = ["doc1", "doc2", "doc3"]

    metrics = evaluate_retrieval(retrieved, expected)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0


def test_evaluate_retrieval_partial():
    """Partial matches should compute precision and recall correctly."""
    retrieved = ["doc1", "doc2", "doc4"]  # doc1, doc2 are correct, doc4 is wrong
    expected = ["doc1", "doc2", "doc3"]  # doc3 was missed

    metrics = evaluate_retrieval(retrieved, expected)
    assert metrics["precision"] == 2 / 3  # 2 correct out of 3 retrieved
    assert metrics["recall"] == 2 / 3  # 2 found out of 3 expected
    assert abs(metrics["f1"] - 2 / 3) < 0.001


def test_evaluate_retrieval_empty():
    """Empty retrievals should not crash."""
    metrics = evaluate_retrieval([], [])
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["f1"] == 0.0
