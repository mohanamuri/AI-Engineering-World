"""
Cross-encoder reranking with LangChain.

Reranking improves answer quality by:
1. Retrieving a larger set of candidates (e.g., 30)
2. Running them through a cross-encoder to score relevance
3. Returning only the top-N (e.g., 5)

This two-stage approach is more cost-effective than increasing top_k at retrieval.
"""

from langchain_community.document_compressors.cross_encoder import CrossEncoderRerank
from langchain.retrievers import ContextualCompressionRetriever


def get_reranker():
    """
    Create a cross-encoder reranker.

    The cross-encoder model is trained to score (query, document) pairs.
    Higher score = more relevant to the query.

    Returns:
        CrossEncoderRerank instance
    """
    return CrossEncoderRerank(
        model="cross-encoder/ms-marco-MiniLM-L-12-v2",  # Efficient model
        top_n=8,  # Return top 8 after reranking
    )


def rerank_documents(retriever, top_k: int = 8):
    """
    Wrap a retriever with cross-encoder reranking.

    This is composition: takes a base retriever and wraps it with compression.

    Args:
        retriever: Base LangChain retriever
        top_k: Number of results after reranking

    Returns:
        Retriever with reranking applied
    """
    compressor = get_reranker()

    # ContextualCompressionRetriever wraps the base retriever
    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=retriever,
    )
