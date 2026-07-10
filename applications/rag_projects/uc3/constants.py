"""Shared constants for RAG Projects — UC3: Agentic RAG."""

NAVIGATION_SESSION_KEY = "rag_uc3_nav"

# Loaded documents: list[LoadedDoc]
DOCS_SESSION_KEY = "rag_uc3_docs"

# Chunked documents: list[Document]
CHUNKS_SESSION_KEY = "rag_uc3_chunks"

# Built vector store: VectorStoreResult
VECTOR_STORE_SESSION_KEY = "rag_uc3_vectorstore"

# Agent RAG config: AgentRAGConfig
RAG_CONFIG_SESSION_KEY = "rag_uc3_config"

# Chat history: list[AgentRAGResult]
CHAT_HISTORY_SESSION_KEY = "rag_uc3_chat_history"
