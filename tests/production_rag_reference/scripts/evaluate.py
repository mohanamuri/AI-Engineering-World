import json
from pathlib import Path
from app.evaluation.evaluator import evaluate_retrieval

dataset = json.loads(Path("app/evaluation/golden_set.json").read_text())
print("Wire your real retrieve_fn, then call:")
print("evaluate_retrieval(dataset, retrieve_fn, k=5)")
