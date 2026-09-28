# Architecture

```text
                   Client / UI
                       |
                 API Gateway
                       |
                OIDC/JWT Auth
                       |
                  FastAPI API
                       |
        +--------------+--------------+
        |              |              |
      Cache        Query Guard     Tracing
        |              |              |
        +--------------+--------------+
                       |
                Tenant + ACL context
                       |
            +----------+----------+
            |                     |
       Dense Retrieval        BM25 Search
            |                     |
            +----------+----------+
                       |
                     RRF
                       |
                 Top-N candidates
                       |
                 Cross-Encoder
                   Reranking
                       |
                 ACL re-check
                       |
               Context builder
                       |
                  Grounded LLM
                       |
               Answer + citations
                       |
             Metrics / Audit / Eval

Offline:
Object Store -> Parse -> Clean -> Chunk -> ACL metadata
           -> Embed -> pgvector/OpenSearch -> versioned index
```
