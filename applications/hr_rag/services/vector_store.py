"""Vector store service for the HR Analytics RAG pipeline.

Wraps ChromaDB in-memory with HuggingFace all-MiniLM-L6-v2 embeddings.
No API key required — embeddings run locally.
"""

from __future__ import annotations
from dataclasses import dataclass

import chromadb
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


@dataclass
class VectorStoreResult:
    vectorstore: Chroma
    chunk_count: int
    embedding_model: str
    collection_name: str = "hr_policy"


def build_vector_store(chunks: list[Document], embedding_model: str = "all-MiniLM-L6-v2") -> VectorStoreResult:
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    client = chromadb.EphemeralClient()
    vectorstore = Chroma.from_documents(
        documents=chunks, embedding=embeddings,
        client=client, collection_name="hr_policy",
    )
    return VectorStoreResult(vectorstore=vectorstore, chunk_count=len(chunks), embedding_model=embedding_model)


def similarity_search(vectorstore: Chroma, query: str, k: int = 4) -> list[Document]:
    return vectorstore.similarity_search(query, k=k)
