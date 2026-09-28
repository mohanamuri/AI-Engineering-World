"""
Document loading with LangChain.

LangChain's document loaders abstract away the complexity of different file formats
(PDF, DOCX, TXT, web, etc.) and provide a unified Document interface.
"""

from pathlib import Path
from langchain_community.document_loaders import (
    TextLoader,
    PDFPlumberLoader,
    Docx2docLoader,
)
from langchain.schema import Document


def load_text_file(path: str) -> list[Document]:
    """
    Load a plain text file.

    Args:
        path: Path to .txt file

    Returns:
        List of LangChain Document objects
    """
    loader = TextLoader(path, encoding="utf-8")
    return loader.load()


def load_pdf_file(path: str) -> list[Document]:
    """
    Load a PDF file using PDFPlumber.

    Args:
        path: Path to .pdf file

    Returns:
        List of LangChain Document objects
    """
    loader = PDFPlumberLoader(path)
    return loader.load()


def load_docx_file(path: str) -> list[Document]:
    """
    Load a Word document.

    Args:
        path: Path to .docx file

    Returns:
        List of LangChain Document objects
    """
    loader = Docx2docLoader(path)
    return loader.load()


def load_documents_from_directory(directory: str) -> list[Document]:
    """
    Load all documents from a directory (multiple formats).

    Supports: .txt, .pdf, .docx

    Args:
        directory: Path to directory containing documents

    Returns:
        List of LangChain Document objects
    """
    documents = []
    dir_path = Path(directory)

    # Load text files
    for txt_file in dir_path.glob("**/*.txt"):
        documents.extend(load_text_file(str(txt_file)))

    # Load PDF files
    for pdf_file in dir_path.glob("**/*.pdf"):
        try:
            documents.extend(load_pdf_file(str(pdf_file)))
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")

    # Load Word documents
    for docx_file in dir_path.glob("**/*.docx"):
        try:
            documents.extend(load_docx_file(str(docx_file)))
        except Exception as e:
            print(f"Error loading {docx_file}: {e}")

    return documents
