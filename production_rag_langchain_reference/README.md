# Production RAG Reference — LangChain Edition

Practical Python reference for a production-style RAG system using **LangChain** (the framework commonly used in real projects).

## Key Differences from Scratch Implementation

| Aspect | Scratch | LangChain |
|--------|---------|-----------|
| **Document Loading** | Manual file I/O | LangChain loaders (PDF, web, etc.) |
| **Chunking** | Custom word-splitter | LangChain TextSplitter (recursive, semantic) |
| **Embeddings** | Manual embedding calls | LangChain Embeddings abstraction |
| **Vector Store** | Custom SQL queries | LangChain Retrievers (Chroma, Pinecone, etc.) |
| **Retrieval** | Manual dense + BM25 | LangChain hybrid retrieval chains |
| **Chains** | Manual prompt + LLM calls | LangChain chains (RetrievalQA, etc.) |
| **Memory/Cache** | Redis custom logic | LangChain memory + caching layers |
| **Callbacks** | Custom tracing | LangChain callbacks framework |

## Pipeline

**Ingestion:**
```
documents -> LangChain loaders -> text splitters -> embeddings -> vector store
```

**Online:**
```
user -> auth -> LangChain retriever chain -> prompt template -> LLM -> citations
```

**Cross-cutting:**
```
security | multi-tenancy | callbacks (tracing/metrics) | caching | evaluation
```

## Project Structure

```
app/
├── core/               # Config, logging, metrics
├── security/           # Auth, RBAC, prompt guards (same as scratch)
├── ingestion/          # Loaders, splitters, embeddings (LangChain-based)
├── retrieval/          # Retrievers, hybrid search, cache (LangChain chains)
├── generation/         # Chains, prompt templates, LLM (LangChain orchestration)
├── models/             # Schemas (same as scratch)
├── observability/      # Callbacks, tracing (LangChain callbacks)
├── evaluation/         # Eval metrics (same structure)
├── api/                # FastAPI routes (same interface)
└── main.py            # FastAPI app
```

## Stack

**Framework:** LangChain + LangSmith (tracing)
**Vectorstores:** Chroma, Pinecone, or PostgreSQL pgvector
**LLM:** OpenAI (via LangChain)
**API:** FastAPI
**Embeddings:** Sentence-Transformers or OpenAI embeddings
**Caching:** LangChain semantic cache + Redis

## Getting Started

See `docs/QUICK_START.md` for setup and `docs/INTERVIEW_MAP.md` for concept-to-code mapping.
