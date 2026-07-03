"""Shared constants for the loan eligibility RAG application."""

NAVIGATION_SESSION_KEY = "loan_rag_navigation"
UPLOAD_PAGE_LABEL = "📄 Load Policy"

# Document session keys
LOAD_RESULT_SESSION_KEY = "loan_rag_load_result"       # LoadResult dataclass
CHUNKS_SESSION_KEY = "loan_rag_chunks"                 # list[Document] after chunking

# Configuration session key
RAG_CONFIG_SESSION_KEY = "loan_rag_config"             # RAGConfig dataclass

# Vector store session key
VECTOR_STORE_SESSION_KEY = "loan_rag_vector_store"     # VectorStoreResult dataclass

# Chat session key
CHAT_HISTORY_SESSION_KEY = "loan_rag_chat_history"     # list[dict]
