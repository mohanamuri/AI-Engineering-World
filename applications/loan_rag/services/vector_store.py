"""
Vector store service for the loan RAG pipeline.

Wraps ChromaDB in-memory with Ollama embeddings (nomic-embed-text).

Why ChromaDB?
--------------
ChromaDB is a lightweight, Python-native vector database designed for
embeddings. It runs entirely in-process (no external server needed) when
using EphemeralClient, which means zero infrastructure for a demo.

Why in-memory (EphemeralClient)?
----------------------------------
Streamlit reruns the script on every interaction. A persistent on-disk
database would accumulate stale collections across reruns and across
users (on a shared deployment). EphemeralClient is recreated fresh each
time the user clicks "Build vector store" — no leftover state.

Why nomic-embed-text?
----------------------
It is a small, fast, open-weights embedding model optimised for semantic
search. It outperforms OpenAI ada-002 on BEIR benchmarks at a fraction of
the cost (free, local, no API key). It runs via Ollama using the same
interface as any other Ollama model.

Interview note — cosine vs L2 distance
----------------------------------------
ChromaDB uses L2 (Euclidean) distance by default. For normalised
embeddings (like those from nomic-embed-text) cosine and L2 produce
the same ranking. If you were using raw unnormalised embeddings, cosine
similarity would be preferable.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import chromadb
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class VectorStoreResult:
    """Holds the built vector store and build-time metadata."""
    vectorstore: Chroma
    chunk_count: int
    embedding_model: str
    collection_name: str = "loan_policy"


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build_vector_store(
    chunks: list[Document],
    embedding_model: str = "nomic-embed-text",
) -> VectorStoreResult:
    """Embed all chunks and store them in a fresh in-memory ChromaDB.

    Args:
        chunks:          List of LangChain Documents from document_loader.chunk_text().
        embedding_model: Ollama model name for embeddings.

    Returns:
        VectorStoreResult with the built Chroma instance and metadata.

    Raises:
        RuntimeError: If Ollama is not reachable or the model is not pulled.
    """
    embeddings = OllamaEmbeddings(model=embedding_model)

    # EphemeralClient = pure in-memory, no disk writes, no server.
    client = chromadb.EphemeralClient()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=client,
        collection_name="loan_policy",
    )

    return VectorStoreResult(
        vectorstore=vectorstore,
        chunk_count=len(chunks),
        embedding_model=embedding_model,
    )


# ---------------------------------------------------------------------------
# Retrieval helper
# ---------------------------------------------------------------------------

def similarity_search(
    vectorstore: Chroma,
    query: str,
    k: int = 4,
) -> list[Document]:
    """Return the top-k most relevant chunks for a query.

    Args:
        vectorstore: Built Chroma instance from build_vector_store().
        query:       Natural language question.
        k:           Number of chunks to retrieve.

    Returns:
        List of Document objects ranked by relevance (most relevant first).
    """
    return vectorstore.similarity_search(query, k=k)
