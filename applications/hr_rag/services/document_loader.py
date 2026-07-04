"""Document loading and chunking for the HR Analytics RAG pipeline.

Handles PDF and plain-text HR policy documents (retention policies,
compensation guidelines, performance review procedures, etc.).
"""

from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class LoadResult:
    raw_text: str
    pages: int
    source_name: str
    word_count: int
    char_count: int


def load_pdf_bytes(file_bytes: bytes, filename: str) -> LoadResult:
    from pypdf import PdfReader
    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages_text = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise ValueError(f"Could not read PDF '{filename}': {exc}") from exc
    raw_text = "\n\n".join(pages_text).strip()
    return LoadResult(raw_text=raw_text, pages=len(reader.pages), source_name=filename,
                      word_count=len(raw_text.split()), char_count=len(raw_text))


def load_txt_bytes(file_bytes: bytes, filename: str) -> LoadResult:
    raw_text = file_bytes.decode("utf-8", errors="replace").strip()
    return LoadResult(raw_text=raw_text, pages=1, source_name=filename,
                      word_count=len(raw_text.split()), char_count=len(raw_text))


def chunk_text(load_result: LoadResult, chunk_size: int = 512, chunk_overlap: int = 64) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""], length_function=len,
    )
    return splitter.create_documents(
        texts=[load_result.raw_text],
        metadatas=[{"source": load_result.source_name}],
    )
