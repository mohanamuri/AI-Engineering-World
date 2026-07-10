"""
Vector store service for RAG Projects.

Identical to the loan_rag vector store — wraps ChromaDB in-memory with
all-MiniLM-L6-v2 HuggingFace embeddings.

The collection name is parameterised so UC1 and future use cases each
get their own isolated ChromaDB collection.
"""

from __future__ import annotations

from dataclasses import dataclass

import chromadb
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


@dataclass
class VectorStoreResult:
    """Holds the built vector store and build-time metadata."""
    vectorstore: Chroma
    chunk_count: int
    doc_count: int
    embedding_model: str
    collection_name: str


def build_vector_store(
    chunks: list[Document],
    doc_count: int,
    collection_name: str = "rag_multi_doc",
    embedding_model: str = "all-MiniLM-L6-v2",
) -> VectorStoreResult:
    """Embed all chunks and store them in a fresh in-memory ChromaDB.

    Args:
        chunks:           LangChain Documents from document_loader.chunk_documents().
        doc_count:        Number of source documents contributing to the chunks.
        collection_name:  ChromaDB collection name (unique per use case).
        embedding_model:  HuggingFace sentence-transformer model name.

    Returns:
        VectorStoreResult with the built Chroma instance and build metadata.
    """
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    client = chromadb.EphemeralClient()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=client,
        collection_name=collection_name,
    )

    return VectorStoreResult(
        vectorstore=vectorstore,
        chunk_count=len(chunks),
        doc_count=doc_count,
        embedding_model=embedding_model,
        collection_name=collection_name,
    )
