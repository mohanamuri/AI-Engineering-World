# Production RAG Reference Application

Reusable Python reference for a production-style RAG system.

## Pipeline

Ingestion:
`documents -> parsing -> cleaning -> chunking -> metadata/ACL -> embeddings -> vector index`

Online:
`user -> auth -> query validation -> cache -> dense + BM25 retrieval -> RRF -> rerank -> ACL -> prompt -> LLM -> citations`

Cross-cutting:
`security | evaluation | observability | retries | caching | tenant isolation`

See `docs/INTERVIEW_MAP.md` for the concept-to-code mapping.
