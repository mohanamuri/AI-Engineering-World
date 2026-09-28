# Production checklist

## Data
- [ ] Stable document/chunk IDs
- [ ] Versioned documents
- [ ] Tenant metadata
- [ ] Owner/role ACL metadata
- [ ] Deletion propagation
- [ ] Re-embedding strategy

## Retrieval
- [ ] Dense retrieval
- [ ] BM25
- [ ] RRF
- [ ] Metadata filters
- [ ] Cross-encoder reranking
- [ ] Deduplication
- [ ] Candidate limits

## Security
- [ ] OIDC/JWT
- [ ] RBAC/ABAC
- [ ] Tenant isolation
- [ ] Data-layer ACL filters
- [ ] Prompt-injection defense
- [ ] PII/secrets redaction
- [ ] Rate limiting
- [ ] Audit logs
- [ ] Encryption
- [ ] Secret manager

## Reliability
- [ ] Timeouts
- [ ] Bounded retries
- [ ] Circuit breaker
- [ ] Fallback strategy
- [ ] Cache
- [ ] Async ingestion
- [ ] Health/readiness probes

## Evaluation
- [ ] Golden question set
- [ ] Recall@K
- [ ] MRR
- [ ] Precision@K
- [ ] NDCG
- [ ] Context precision/recall
- [ ] Faithfulness/groundedness
- [ ] Answer relevance
- [ ] Citation correctness
- [ ] CI regression threshold

## Observability
- [ ] Request count
- [ ] p50/p95/p99 latency
- [ ] Retrieval latency
- [ ] Reranker latency
- [ ] LLM latency
- [ ] Token usage/cost
- [ ] Cache hit rate
- [ ] Retrieved chunk count
- [ ] Context size
- [ ] Model/version
- [ ] Evaluation scores
