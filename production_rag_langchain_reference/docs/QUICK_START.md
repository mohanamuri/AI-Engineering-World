# Quick Start

Get the LangChain RAG system running locally in 5 minutes.

## Prerequisites

- Python 3.11+
- OpenAI API key
- Redis (or in-memory fallback)

## Installation

```bash
# Clone and navigate to project
cd production_rag_langchain_reference

# Install dependencies
pip install -e .

# Create .env file
cp .env.example .env

# Edit .env with your API key
export OPENAI_API_KEY="sk-..."
```

## 1. Run Locally (Development)

```bash
# Start Redis (if you have Docker)
docker run -d -p 6379:6379 redis:latest

# Start the API server
python -m uvicorn app.main:app --reload --port 8000

# API available at http://localhost:8000
```

## 2. Load Documents (Ingestion)

Create a simple ingestion script:

```python
from app.ingestion.loaders import load_documents_from_directory
from app.ingestion.chunker import split_documents
from app.retrieval.vectorstore import index_documents

# Load documents
docs = load_documents_from_directory("./data")

# Split into chunks
chunks = split_documents(docs)

# Index in vectorstore
index_documents(chunks, tenant_id="demo-tenant")

print(f"Indexed {len(chunks)} chunks")
```

Save as `scripts/ingest.py` and run:
```bash
python scripts/ingest.py
```

## 3. Query the API

```bash
curl -X POST "http://localhost:8000/v1/ask" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -H "X-Tenant-ID: demo-tenant" \
  -H "X-Roles: employee" \
  -d '{
    "question": "What is a RAG system?",
    "top_k": 5
  }'
```

Response:
```json
{
  "answer": "A Retrieval-Augmented Generation (RAG) system...",
  "citations": [
    {
      "chunk_id": "...",
      "title": "RAG Overview",
      "source": "documents/rag-intro.pdf"
    }
  ],
  "cached": false,
  "trace_id": "abc123..."
}
```

## 4. Check Health & Metrics

```bash
# Health check
curl http://localhost:8000/health

# Prometheus metrics
curl http://localhost:8000/metrics
```

## Configuration

Edit `app/core/config.py` or `.env`:

```env
# LLM
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o-mini

# Embeddings (HuggingFace or OpenAI)
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# Vectorstore
CHROMA_PERSISTENCE_PATH=./chroma_db
CHROMA_COLLECTION_NAME=rag_documents

# Redis (for caching)
REDIS_URL=redis://localhost:6379
CACHE_TTL_SECONDS=3600

# RAG parameters
CHUNK_SIZE=700
CHUNK_OVERLAP=100
TOP_K_RETRIEVAL=8

# Security
DEV_AUTH_ENABLED=true  # Set to false for production
```

## Docker Deployment

```bash
# Build image
docker build -t production-rag-langchain .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="sk-..." \
  -e REDIS_URL="redis://redis-host:6379" \
  production-rag-langchain
```

## Next Steps

- See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed design
- See [INTERVIEW_MAP.md](./INTERVIEW_MAP.md) for concept-to-code mapping
- Check `tests/` for examples
- Review `docs/docker-compose.yml` for full stack setup
