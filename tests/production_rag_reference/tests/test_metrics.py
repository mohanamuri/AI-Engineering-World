from app.evaluation.metrics import recall_at_k, mrr

def test_recall():
    assert recall_at_k(["a", "b"], ["b"], 2) == 1.0

def test_mrr():
    assert mrr(["x", "b"], ["b"]) == 0.5
