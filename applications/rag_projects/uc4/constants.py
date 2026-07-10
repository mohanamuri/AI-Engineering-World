"""Shared constants for RAG Projects — UC4: Self-RAG."""

NAVIGATION_SESSION_KEY = "rag_uc4_nav"

# Loaded documents: list[LoadedDoc]
DOCS_SESSION_KEY = "rag_uc4_docs"

# Chunked documents: list[Document]
CHUNKS_SESSION_KEY = "rag_uc4_chunks"

# Built vector store: VectorStoreResult
VECTOR_STORE_SESSION_KEY = "rag_uc4_vectorstore"

# Self-RAG config: SelfRAGConfig
RAG_CONFIG_SESSION_KEY = "rag_uc4_config"

# Chat history: list[SelfRAGResult]
CHAT_HISTORY_SESSION_KEY = "rag_uc4_chat_history"
