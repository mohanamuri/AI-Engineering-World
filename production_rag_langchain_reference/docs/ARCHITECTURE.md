# Architecture

LangChain edition of the Production RAG Reference, showing how real projects build RAGs with frameworks.

## Key Differences from Scratch Version

| Aspect | Scratch | LangChain |
|--------|---------|-----------|
| **Components** | Custom implementations | LangChain abstractions |
| **Loaders** | Manual file I/O | LangChain community loaders |
| **Splitting** | Custom word-splitter | `RecursiveCharacterTextSplitter` |
| **Embeddings** | Direct calls | LangChain `Embeddings` interface |
| **Vectorstore** | SQL queries | LangChain Chroma/Pinecone/Weaviate |
| **Retrieval** | Manual BM25 + dense | LangChain `Retriever` interface |
| **Chains** | Manual orchestration | LangChain `RetrievalQA` chains |
| **Reranking** | Custom integration | `ContextualCompressionRetriever` |
| **Callbacks** | Custom tracing | LangChain `Callback` system |

## Data Flow

```
                      Client/API
                          |
                    FastAPI Router
                          |
                  [Auth] [Rate Limit] [Log]
                          |
                    Query Validation
                          |
                    Cache Check
                     /         \
                   HIT          MISS
                    |           |
                   Return    Retriever
                         (with tenant filter)
                             |
                      Reranker
                    (cross-encoder)
                             |
                      ACL Re-check
                             |
                     RAGChain (LLM)
                             |
                      Format Response
                             |
                     Cache & Return
```

## LangChain Integration Points

### 1. Loaders (`app/ingestion/loaders.py`)
```python
from langchain_community.document_loaders import TextLoader, PDFPlumberLoader
loader = PDFPlumberLoader("document.pdf")
docs = loader.load()  # Returns List[Document]
```

### 2. Text Splitters (`app/ingestion/chunker.py`)
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
chunks = splitter.split_documents(docs)
```

### 3. Embeddings (`app/ingestion/embedder.py`)
```python
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
vectors = embeddings.embed_documents(texts)
```

### 4. Vectorstore (`app/retrieval/vectorstore.py`)
```python
from langchain_chroma import Chroma
vectorstore = Chroma(collection_name="documents", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
```

### 5. Reranking (`app/retrieval/reranker.py`)
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors.cross_encoder import CrossEncoderRerank
compressor = CrossEncoderRerank(model="cross-encoder/ms-marco-MiniLM-L-12-v2")
reranker = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
```

### 6. Chains (`app/generation/llm.py`)
```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)
```

## Security & Multi-tenancy

**Tenant Isolation:**
- Metadata filter at retrieval time: `{"tenant_id": tenant_id}`
- Second ACL check before generation (defense-in-depth)

**Prompt Injection Prevention:**
- Query sanitization
- System message injection (cannot be overridden)

## Observability

**Tracing:** Correlation ID (trace_id) flows through entire request
**Metrics:** Prometheus metrics for monitoring
**Logging:** Structured logs with trace_id and operation context

## Comparison: When to Use Each

### Use This (LangChain) When:
- Building production systems with teams (proven patterns)
- Need multi-document format support (PDF, DOCX, etc.)
- Want framework abstractions (easily swap vectorstores)
- Prefer composition over custom code
- Need callbacks and built-in observability

### Use Scratch Version When:
- Learning RAG internals (great educational reference)
- Building simple single-purpose systems
- Want maximum control over every component
- Prefer minimal dependencies
- Evaluating novel retrieval strategies
