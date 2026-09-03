# RAG Architecture

## Core flow
### Ingestion
Load → normalize → split/chunk → metadata → embeddings → index/vector store.

### Retrieval
Query → optional rewrite → query embedding/keyword query → candidate retrieval → filtering/reranking/RRF → context assembly.

### Generation
Prompt/context → LLM → structured answer → validation/evaluation → response.

The user's resume specifically describes Hybrid Search using BM25 + semantic vector search with RRF and a Self-RAG critique loop. fileciteturn0file0L25-L32

## Architect-level topics
- Chunking strategy
- Metadata and access-control filtering
- Hybrid retrieval
- Reranking
- RRF
- Query rewriting
- Multi-query retrieval
- Context compression
- Parent-child retrieval
- Citation/grounding
- Caching
- Evaluation
- Freshness and re-indexing
- Multi-tenant isolation

## Key metrics
Retrieval: Recall@K, Precision@K, MRR/nDCG.
Generation: groundedness, relevance, completeness, answer correctness.
System: latency, throughput, error rate, cost/request.

## Interview coding expectation
Be able to write a minimal pipeline without relying entirely on framework magic.
