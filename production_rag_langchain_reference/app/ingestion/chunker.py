"""
Text chunking with LangChain text splitters.

LangChain provides multiple splitting strategies:
- RecursiveCharacterTextSplitter: hierarchical splitting (good for code/documents)
- CharacterTextSplitter: simple character-based split
- TokenTextSplitter: split by token count (better for LLMs)
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from app.core.config import get_settings


def get_text_splitter():
    """
    Create a configured text splitter instance.

    Uses RecursiveCharacterTextSplitter which is the most robust for
    general-purpose document splitting. It tries to split at logical
    boundaries (paragraph, sentence, word) before falling back to characters.

    Returns:
        Configured RecursiveCharacterTextSplitter instance
    """
    settings = get_settings()

    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],  # Try splitting at these boundaries
        length_function=len,
    )


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split documents into chunks using LangChain's text splitter.

    Each chunk retains metadata from the original document:
    - source: file path
    - title: document title (if available)
    - chunk_index: position in document

    Args:
        documents: List of LangChain Document objects

    Returns:
        List of chunked Document objects with preserved metadata
    """
    splitter = get_text_splitter()

    # split_documents automatically preserves metadata
    chunked = splitter.split_documents(documents)

    # Add chunk_index metadata to each chunk
    for i, chunk in enumerate(chunked):
        chunk.metadata["chunk_index"] = i

    return chunked
