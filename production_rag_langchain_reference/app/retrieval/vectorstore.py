"""
Vector store management with LangChain.

LangChain abstracts different vector databases:
- Chroma: local, open-source, great for development
- Pinecone: managed, cloud-based
- Weaviate: GraphQL-based
- Milvus: open-source, scalable

This example uses Chroma for simplicity.
"""

from langchain_chroma import Chroma
from langchain.schema import Document
from app.core.config import get_settings
from app.ingestion.embedder import get_embeddings


def get_vector_store():
    """
    Get or create a Chroma vector store instance.

    Chroma persists to disk and can be easily swapped for other vectorstores.

    Returns:
        Chroma vector store instance
    """
    settings = get_settings()
    embeddings = get_embeddings()

    return Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_persistence_path,
    )


def index_documents(documents: list[Document], tenant_id: str):
    """
    Add documents to the vector store.

    Metadata (tenant_id, roles) is stored for filtering at retrieval time.

    Args:
        documents: List of chunked Document objects with metadata
        tenant_id: Tenant ID for multi-tenancy isolation
    """
    vectorstore = get_vector_store()

    # Add tenant_id to metadata for all documents
    for doc in documents:
        if "tenant_id" not in doc.metadata:
            doc.metadata["tenant_id"] = tenant_id

    # Add to vector store
    vectorstore.add_documents(documents)


def get_retriever(tenant_id: str, top_k: int = 8):
    """
    Get a configured retriever for a specific tenant.

    The retriever filters by tenant_id at search time (first ACL check).

    Args:
        tenant_id: Tenant ID to filter results by
        top_k: Number of results to return

    Returns:
        LangChain Retriever instance
    """
    vectorstore = get_vector_store()

    # Create retriever with metadata filtering
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": top_k,
            "filter": {"tenant_id": tenant_id},  # Multi-tenancy filter
        },
    )


def delete_tenant_documents(tenant_id: str):
    """
    Delete all documents for a tenant (for data deletion/GDPR).

    Args:
        tenant_id: Tenant ID to delete
    """
    vectorstore = get_vector_store()

    # Chroma doesn't have bulk delete by filter, so we'd need to iterate
    # In production, use a database that supports this natively
    # For now, this is a placeholder
    pass
