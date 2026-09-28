# Scratch vs LangChain: Quick Comparison

This repository contains **TWO complementary RAG reference implementations**:

1. **`production_rag_reference/`** — From-scratch implementation
2. **`production_rag_langchain_reference/`** — LangChain framework implementation

## When to Use Each

### Use the Scratch Version When:

✓ **Learning RAG internals** — Every component is explicit  
✓ **Teaching others** — Great for understanding the "why"  
✓ **Prototyping novel techniques** — You need full control  
✓ **Minimal dependencies** — Prefer fewer libraries  
✓ **Specific performance requirements** — Tune every detail  

**Examples:**
- Academic research
- Building from first principles
- Optimizing for specific constraints

### Use the LangChain Version When:

✓ **Building production systems** — Proven patterns, less code  
✓ **Working in teams** — Standard abstractions = easier handoffs  
✓ **Multiple document formats** — PDF, DOCX, web loaders included  
✓ **Swapping components easily** — Vectorstore-agnostic  
✓ **Time-to-market matters** — 3x faster development  

**Examples:**
- Enterprise Q&A systems
- Startup MVP
- Multi-tenant SaaS
- Integration with other LangChain tools

## Side-by-Side Comparison

| Aspect | Scratch | LangChain |
|--------|---------|-----------|
| **Lines of code** | ~500 | ~400 (less boilerplate) |
| **Learning curve** | Steep (learn RAG) | Shallow (learn framework) |
| **Document loaders** | Manual | 50+ pre-built |
| **Text splitters** | Custom word-split | Recursive, semantic, token-aware |
| **Embeddings** | Direct OpenAI/HF calls | Unified interface |
| **Vectorstore** | SQL queries | Abstract retriever interface |
| **Retrieval** | Custom dense + BM25 | Built-in hybrid + reranking |
| **Chains** | Manual prompt + LLM | Composition-based chains |
| **Callbacks** | Custom tracing | Native callback system |
| **Dependency mgmt** | Simpler | More complex (but managed) |
| **Flexibility** | Maximum | High (composable) |
| **Production-ready** | Yes (with care) | Yes (out-of-box) |

## Code Examples

### Loading Documents

**Scratch:**
```python
def load_text_file(path):
    return Path(path).read_text(encoding="utf-8")
```

**LangChain:**
```python
from langchain_community.document_loaders import PDFPlumberLoader
loader = PDFPlumberLoader("file.pdf")
docs = loader.load()
```

LangChain wins: handles 50+ formats, preserves metadata.

### Text Splitting

**Scratch:**
```python
words = text.split()
chunks = [" ".join(words[i:i+chunk_size]) 
          for i in range(0, len(words), chunk_size - overlap)]
```

**LangChain:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
chunks = splitter.split_documents(docs)
```

LangChain wins: respects logical boundaries (paragraphs, sentences).

### Retrieval

**Scratch:**
```python
# Manual dense + BM25 + RRF
dense_results = vector_db.search(query_embedding)
sparse_results = bm25.get_top_k(query)
rrf_results = reciprocal_rank_fusion([dense_results, sparse_results])
```

**LangChain:**
```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
docs = retriever.get_relevant_documents(query)
```

Scratch wins: more control. LangChain wins: simplicity + extensibility.

### Generation

**Scratch:**
```python
prompt = build_prompt(question, context)
answer = llm.generate(prompt)
```

**LangChain:**
```python
from langchain.chains import RetrievalQA
chain = RetrievalQA.from_chain_type(
    llm=llm, retriever=retriever, chain_type="stuff"
)
answer = chain.invoke({"query": question})
```

LangChain wins: automatic prompt building, citations, error handling.

## Architecture

### Scratch
```
User Query
    ↓
Custom Routes (FastAPI)
    ↓
Manual Orchestration
    ├→ Retrieval (custom dense + BM25)
    ├→ Prompt Building
    ├→ LLM Call
    └→ Response
```

### LangChain
```
User Query
    ↓
FastAPI Routes
    ↓
LangChain Chain (RetrievalQA)
    ├→ Retriever (pluggable)
    ├→ PromptTemplate
    ├→ LLM (pluggable)
    └→ Output Parser
    
    (Callbacks at each step)
```

LangChain's approach is **composable** and **extensible**.

## Migration Path

If you start with **Scratch** and want to scale:

1. Keep your auth, security, and evaluation code
2. Replace ingestion with LangChain loaders
3. Replace retrieval with LangChain retrievers + reranker
4. Replace generation with LangChain chains
5. Gain all the benefits of the ecosystem

**Zero breaking changes to your API.**

## Real-World Examples

### Scratch Version Usage
- Educational courses
- Research papers
- Custom optimization projects

### LangChain Version Usage
- **OpenAI:** ChatGPT plugins
- **Vercel:** AI SDK examples
- **Anthropic:** Claude API tutorials
- **LangChain:** Official docs + LangSmith

## Learning Recommendation

**Best approach:**
1. **First:** Study the Scratch version (understand RAG)
2. **Then:** Study the LangChain version (understand frameworks)
3. **Finally:** Build production systems with LangChain (or customize as needed)

Both implementations are **equally production-ready**, just solving different problems.

---

**For interviews:** Understand both approaches. Scratch shows deep knowledge, LangChain shows practical expertise.
