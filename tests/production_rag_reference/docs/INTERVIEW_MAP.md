# RAG concept -> code

| Concept | File |
|---|---|
| Loading | `app/ingestion/loaders.py` |
| Chunking | `app/ingestion/chunker.py` |
| Embeddings | `app/ingestion/embedder.py` |
| Sparse retrieval / BM25 | `app/retrieval/bm25.py` |
| Hybrid retrieval | `app/retrieval/hybrid.py` |
| RRF | `app/retrieval/hybrid.py` |
| Reranking | `app/retrieval/reranker.py` |
| Cache | `app/retrieval/cache.py` |
| Prompt | `app/generation/prompt.py` |
| LLM | `app/generation/llm.py` |
| Authentication | `app/security/auth.py` |
| RBAC / tenant isolation | `app/security/access_control.py` |
| Prompt injection | `app/security/prompt_guard.py` |
| Retrieval evaluation | `app/evaluation/*` |
| Tracing | `app/observability/tracing.py` |
| Metrics | `app/core/metrics.py` |
| API | `app/api/routes.py` |

## Interview mental model

A production RAG is not simply `query -> vector DB -> LLM`.

It is:

1. ingest
2. parse
3. clean
4. chunk
5. enrich metadata
6. embed
7. index
8. authenticate
9. authorize
10. validate query
11. retrieve dense + sparse
12. fuse with RRF
13. rerank
14. apply ACL again
15. construct bounded context
16. generate grounded answer
17. return citations
18. cache safely
19. trace/measure
20. continuously evaluate

## Advanced concepts to add later

- query rewriting / multi-query retrieval
- HyDE
- parent-child retrieval
- contextual compression
- metadata/freshness filters
- semantic cache
- model routing
- streaming
- async ingestion queues
- document versioning
- deletion propagation
- PII redaction
- secret scanning
- OIDC/JWT + RBAC/ABAC
- row-level security
- rate limiting
- circuit breakers
- OpenTelemetry
- RAGAS/DeepEval-style generation evaluation
- CI regression gates
