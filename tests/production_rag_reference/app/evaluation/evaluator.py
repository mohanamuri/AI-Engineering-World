from app.evaluation.metrics import recall_at_k, mrr, precision_at_k

def evaluate_retrieval(dataset, retrieve_fn, k=5):
    recalls, mrrs, precisions = [], [], []
    for row in dataset:
        results = retrieve_fn(row["question"])
        ids = [r.chunk.id for r in results]
        relevant = row["relevant_chunk_ids"]
        recalls.append(recall_at_k(ids, relevant, k))
        mrrs.append(mrr(ids, relevant))
        precisions.append(precision_at_k(ids, relevant, k))
    n = len(dataset) or 1
    return {
        "recall_at_k": sum(recalls) / n,
        "mrr": sum(mrrs) / n,
        "precision_at_k": sum(precisions) / n,
    }
