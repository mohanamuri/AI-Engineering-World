def recall_at_k(retrieved_ids, relevant_ids, k):
    if not relevant_ids:
        return 0.0
    return len(set(retrieved_ids[:k]) & set(relevant_ids)) / len(set(relevant_ids))

def mrr(retrieved_ids, relevant_ids):
    relevant_ids = set(relevant_ids)
    for rank, item_id in enumerate(retrieved_ids, start=1):
        if item_id in relevant_ids:
            return 1.0 / rank
    return 0.0

def precision_at_k(retrieved_ids, relevant_ids, k):
    if k == 0:
        return 0.0
    return len(set(retrieved_ids[:k]) & set(relevant_ids)) / k
