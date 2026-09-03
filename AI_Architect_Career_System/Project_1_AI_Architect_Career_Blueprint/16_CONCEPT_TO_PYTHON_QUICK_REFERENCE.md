# Concept → Python Code Quick Reference

Goal: interviewer-ready recall. Each item should be explainable and implementable from first principles.

## 1. Basic RAG skeleton
```python
docs = load_documents(path)
chunks = split_documents(docs)
vectors = embed(chunks)
index = build_vector_index(vectors)

query = user_input()
qvec = embed([query])
context = index.search(qvec, top_k=5)

prompt = build_prompt(context, query)
answer = llm.generate(prompt)
```

## 2. Cosine similarity
```python
import numpy as np

def cosine_similarity(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
```

## 3. Simple top-k retrieval
```python
def top_k(query_vector, vectors, k=5):
    scored = [(cosine_similarity(query_vector, v), i)
              for i, v in enumerate(vectors)]
    return [i for _, i in sorted(scored, reverse=True)[:k]]
```

## 4. Reciprocal Rank Fusion (RRF)
```python
from collections import defaultdict

def rrf(rank_lists, k=60):
    scores = defaultdict(float)
    for ranking in rank_lists:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] += 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)
```

## 5. Tool-calling mental model
```python
tool = {
    "name": "get_ticket",
    "description": "Fetch a ticket by ID",
    "input_schema": {"type": "object",
                     "properties": {"ticket_id": {"type": "string"}},
                     "required": ["ticket_id"]}
}
```

## 6. Bounded agent loop
```python
for step in range(max_steps):
    decision = model_decide(state, tools)
    if decision["type"] == "final":
        return decision["answer"]
    result = execute_tool(decision["tool"], decision["args"])
    state.append({"tool_result": result})
raise RuntimeError("Agent exceeded max_steps")
```

## 7. Parallel fan-out/fan-in
```python
from concurrent.futures import ThreadPoolExecutor

def fan_out(tasks, worker):
    with ThreadPoolExecutor(max_workers=len(tasks)) as ex:
        results = list(ex.map(worker, tasks))
    return synthesize(results)
```

## 8. Minimal evaluation
```python
def evaluate(expected, actual):
    return {
        "exact_match": expected.strip().lower() == actual.strip().lower(),
        "length": len(actual)
    }
```

## Framework mapping
Learn the framework implementation after understanding the primitive:
- LangChain: components/retrievers/tools/chains
- LangGraph: explicit state + graph orchestration
- LlamaIndex: data/RAG abstractions
- FastAPI: service/API layer
- Vector DB: persistent similarity search
- MCP: standardized tool/resource interface

## Rule
Do not memorize framework syntax as the primary skill. Be able to reconstruct the primitive in plain Python first.
