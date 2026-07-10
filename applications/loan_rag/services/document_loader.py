"""
Document loading and chunking service for the loan RAG pipeline.

Two responsibilities:
  1. Parse raw bytes from a PDF or plain-text file into a clean string.
  2. Split that string into overlapping chunks using LangChain's
     RecursiveCharacterTextSplitter.

Why RecursiveCharacterTextSplitter?
-------------------------------------
It tries to split at paragraph breaks (\\n\\n) first, then newlines,
then sentences, then words. This preserves semantic units as much as
possible — far better than a naive fixed-size slicer.

Why overlapping chunks?
------------------------
A question may straddle the boundary between two chunks (e.g. a table
that spans two paragraphs). A small overlap (e.g. 100 characters) lets
both neighbouring chunks carry that shared context so the retriever
doesn't miss it.

Interview note — pdf vs pypdf vs pdfplumber
---------------------------------------------
pypdf is lightweight and works well for text-heavy PDFs.
pdfplumber is better for PDFs with complex tables and column layouts
but adds a heavier dependency. For a policy document (plain paragraphs)
pypdf is sufficient and keeps requirements slim.
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
class LoadResult:
    """Raw parsed document before chunking."""
    raw_text: str
    pages: int
    source_name: str
    word_count: int
    char_count: int


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_pdf_bytes(file_bytes: bytes, filename: str) -> LoadResult:
    """Parse PDF bytes into plain text using pypdf.

    Each page is extracted separately and joined with a blank line so
    that the subsequent chunker can still detect page boundaries.
    """
    from pypdf import PdfReader  # deferred: only imported when PDF is loaded

    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages_text = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise ValueError(
            f"Could not read PDF '{filename}': {exc}. "
            "Try re-generating the file or use a different PDF."
        ) from exc
    raw_text = "\n\n".join(pages_text).strip()

    return LoadResult(
        raw_text=raw_text,
        pages=len(reader.pages),
        source_name=filename,
        word_count=len(raw_text.split()),
        char_count=len(raw_text),
    )


def load_txt_bytes(file_bytes: bytes, filename: str) -> LoadResult:
    """Decode a plain-text file into a LoadResult."""
    raw_text = file_bytes.decode("utf-8", errors="replace").strip()

    return LoadResult(
        raw_text=raw_text,
        pages=1,
        source_name=filename,
        word_count=len(raw_text.split()),
        char_count=len(raw_text),
    )


def load_default_policy() -> LoadResult:
    """Load the bundled loan_policy.pdf from the repo's data/ directory.

    Returns a LoadResult so the rest of the pipeline treats it identically
    to a user-uploaded file.
    """
    from pathlib import Path

    policy_path = Path(__file__).resolve().parents[4] / "data" / "loan_docs" / "loan_policy.pdf"
    if not policy_path.exists():
        raise FileNotFoundError(
            f"Default policy PDF not found at {policy_path}. "
            "Run: python scripts/generate_policy_pdf.py"
        )
    return load_pdf_bytes(policy_path.read_bytes(), "loan_policy.pdf")


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------

def chunk_text(
    load_result: LoadResult,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[Document]:
    """Split a LoadResult's raw text into overlapping LangChain Documents.

    Args:
        load_result:    The parsed document.
        chunk_size:     Maximum characters per chunk.
        chunk_overlap:  Characters of overlap between consecutive chunks.

    Returns:
        List of LangChain Document objects, each with a ``source`` metadata
        field carrying the original filename.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = splitter.create_documents(
        texts=[load_result.raw_text],
        metadatas=[{"source": load_result.source_name}],
    )
    return chunks
