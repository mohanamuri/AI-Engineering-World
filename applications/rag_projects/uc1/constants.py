"""Shared constants for RAG Projects — UC1: Multi-Document RAG."""

NAVIGATION_SESSION_KEY = "rag_uc1_nav"

# Loaded documents: list[LoadedDoc]
DOCS_SESSION_KEY = "rag_uc1_docs"

# Chunked documents: list[Document]
CHUNKS_SESSION_KEY = "rag_uc1_chunks"

# Built vector store: VectorStoreResult
VECTOR_STORE_SESSION_KEY = "rag_uc1_vectorstore"

# RAG config: RAGConfig
RAG_CONFIG_SESSION_KEY = "rag_uc1_config"

# Chat history: list[RAGResult]
CHAT_HISTORY_SESSION_KEY = "rag_uc1_chat_history"
