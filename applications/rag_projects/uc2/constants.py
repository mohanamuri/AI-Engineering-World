"""Shared constants for RAG Projects — UC2: Hybrid Search RAG."""

NAVIGATION_SESSION_KEY = "rag_uc2_nav"

# Loaded documents: list[LoadedDoc]
DOCS_SESSION_KEY = "rag_uc2_docs"

# Chunked documents: list[Document]
CHUNKS_SESSION_KEY = "rag_uc2_chunks"

# Built vector store: VectorStoreResult
VECTOR_STORE_SESSION_KEY = "rag_uc2_vectorstore"

# BM25 retriever: BM25Retriever
BM25_RETRIEVER_SESSION_KEY = "rag_uc2_bm25"

# Hybrid RAG config: HybridRAGConfig
RAG_CONFIG_SESSION_KEY = "rag_uc2_config"

# Chat history: list[HybridRAGResult]
CHAT_HISTORY_SESSION_KEY = "rag_uc2_chat_history"
