"""
Embedding models with LangChain.

LangChain abstracts different embedding providers:
- HuggingFace: local, fast, free (sentence-transformers)
- OpenAI: powerful, API-based
- Cohere: commercial alternative
"""

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings
from app.core.config import get_settings


def get_embeddings():
    """
    Get the configured embedding model.

    Production decision: Choose based on your priorities
    - HuggingFace: Privacy (local), cost (free), control (open-source)
    - OpenAI: Quality, simplicity, but vendor lock-in and cost

    Returns:
        LangChain Embeddings instance (HuggingFace or OpenAI)
    """
    settings = get_settings()

    # Using HuggingFace embeddings (local, free, good quality)
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": "cpu"},  # Use "cuda" if GPU available
        encode_kwargs={
            "normalize_embeddings": True,
            "batch_size": settings.embedding_batch_size,
        },
    )

    # Alternatively, use OpenAI embeddings (uncomment if preferred):
    # return OpenAIEmbeddings(
    #     model="text-embedding-3-small",
    #     api_key=settings.openai_api_key,
    # )


def embed_documents(documents: list, embeddings) -> list:
    """
    Embed a batch of documents.

    In production, embedding is typically done during ingestion pipeline,
    and the embeddings are stored in the vector database.
    This function is for reference and for standalone embedding operations.

    Args:
        documents: List of text documents or LangChain Documents
        embeddings: Embeddings model instance

    Returns:
        List of embedding vectors
    """
    # Convert to text if LangChain Documents
    texts = [doc.page_content if hasattr(doc, "page_content") else doc for doc in documents]

    # Batch embed
    return embeddings.embed_documents(texts)


def embed_query(query: str, embeddings) -> list[float]:
    """
    Embed a single query for retrieval.

    Args:
        query: User query string
        embeddings: Embeddings model instance

    Returns:
        Embedding vector
    """
    return embeddings.embed_query(query)
