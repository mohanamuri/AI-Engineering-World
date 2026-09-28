#!/usr/bin/env python
"""
Evaluation script: Test RAG quality against golden set.

Usage:
    python scripts/evaluate.py --endpoint http://localhost:8000
"""

import argparse
import requests
import json
from app.evaluation.evaluator import load_golden_set, evaluate_retrieval
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Evaluate RAG system")
    parser.add_argument(
        "--endpoint",
        default="http://localhost:8000",
        help="RAG API endpoint",
    )
    parser.add_argument(
        "--user-id",
        default="eval-user",
        help="User ID for requests",
    )
    parser.add_argument(
        "--tenant-id",
        default="demo-tenant",
        help="Tenant ID for requests",
    )
    args = parser.parse_args()

    # Load golden set
    logger.info("loading_golden_set")
    golden_set = load_golden_set()

    if not golden_set:
        logger.warning("golden_set_empty")
        return 0

    # Evaluate each example
    results = []
    for i, example in enumerate(golden_set, 1):
        logger.info("evaluating", example_num=i, question=example.question)

        # Make API call
        headers = {
            "X-User-ID": args.user_id,
            "X-Tenant-ID": args.tenant_id,
            "X-Roles": "employee",
        }
        payload = {"question": example.question, "top_k": 5}

        try:
            response = requests.post(
                f"{args.endpoint}/v1/ask",
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
        except Exception as e:
            logger.error("api_error", error=str(e))
            continue

        data = response.json()

        # Extract retrieved document IDs
        retrieved_ids = [c["chunk_id"] for c in data.get("citations", [])]

        # Evaluate retrieval quality
        metrics = evaluate_retrieval(retrieved_ids, example.expected_source_ids)

        result = {
            "question": example.question,
            "answer": data.get("answer", ""),
            "retrieval_precision": metrics["precision"],
            "retrieval_recall": metrics["recall"],
            "retrieval_f1": metrics["f1"],
        }
        results.append(result)
        logger.info("evaluation_complete", **result)

    # Summary
    if results:
        avg_precision = sum(r["retrieval_precision"] for r in results) / len(results)
        avg_recall = sum(r["retrieval_recall"] for r in results) / len(results)
        avg_f1 = sum(r["retrieval_f1"] for r in results) / len(results)

        print(f"\n=== RAG Evaluation Results ===")
        print(f"Precision: {avg_precision:.3f}")
        print(f"Recall:    {avg_recall:.3f}")
        print(f"F1 Score:  {avg_f1:.3f}")
        print(f"\nDetailed results: {json.dumps(results, indent=2)}")

    return 0


if __name__ == "__main__":
    exit(main())
