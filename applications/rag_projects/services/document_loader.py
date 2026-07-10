"""
Multi-document loader and chunker for RAG Projects.

Key difference from the single-document loan_rag loader:
  - Accepts a list of (bytes, filename) pairs.
  - Every chunk carries source metadata ({source: filename}) so that
    the chat interface can show which document each answer came from.
  - Exposes a convenience function to chunk all documents together into
    one unified list of LangChain Documents ready for embedding.

Why source metadata?
---------------------
When a user asks "What is the refund policy?" and you have a 10-doc
corpus, returning just the answer is not enough. Showing the source
document name lets the user verify and trust the answer — and immediately
navigate to the right document if they want more context.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class LoadedDoc:
    """One parsed document before chunking."""
    name: str
    raw_text: str
    pages: int
    word_count: int
    char_count: int


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_pdf_bytes(file_bytes: bytes, filename: str) -> LoadedDoc:
    """Parse PDF bytes into a LoadedDoc using pypdf."""
    from pypdf import PdfReader  # deferred: only when a PDF is actually loaded

    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages_text = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise ValueError(
            f"Could not read PDF '{filename}': {exc}. "
            "Try re-generating the file or use a different PDF."
        ) from exc

    raw_text = "\n\n".join(pages_text).strip()
    return LoadedDoc(
        name=filename,
        raw_text=raw_text,
        pages=len(reader.pages),
        word_count=len(raw_text.split()),
        char_count=len(raw_text),
    )


def load_txt_bytes(file_bytes: bytes, filename: str) -> LoadedDoc:
    """Decode a plain-text file into a LoadedDoc."""
    raw_text = file_bytes.decode("utf-8", errors="replace").strip()
    return LoadedDoc(
        name=filename,
        raw_text=raw_text,
        pages=1,
        word_count=len(raw_text.split()),
        char_count=len(raw_text),
    )


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------

def chunk_documents(
    docs: list[LoadedDoc],
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[Document]:
    """Split all documents into overlapping LangChain Documents.

    Each chunk carries ``{"source": doc.name}`` metadata so retrieval
    results can be traced back to their origin document.

    Args:
        docs:          List of LoadedDoc instances (from load_pdf_bytes / load_txt_bytes).
        chunk_size:    Maximum characters per chunk.
        chunk_overlap: Characters of overlap between consecutive chunks.

    Returns:
        A flat list of LangChain Documents from all input documents combined.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    all_chunks: list[Document] = []
    for doc in docs:
        chunks = splitter.create_documents(
            texts=[doc.raw_text],
            metadatas=[{"source": doc.name}],
        )
        all_chunks.extend(chunks)

    return all_chunks
