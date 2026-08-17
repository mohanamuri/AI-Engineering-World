"""Loan RAG — FastAPI router.

Document Q&A pipeline: upload → configure → chat → history
Uses ChromaDB + HuggingFace embeddings + Groq LLM.

Prefix: /api/loan-rag
"""

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from api.session_store import Session, SessionNotFound, create_session, require_session
from applications.loan_rag.services.document_loader import (
    chunk_text, load_pdf_bytes, load_txt_bytes,
)
from applications.loan_rag.services.vector_store import build_vector_store
from applications.loan_rag.services.rag_chain import RAGConfig, run_rag_query

router = APIRouter(prefix="/api/loan-rag", tags=["Loan RAG"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    session_id: str
    filename: str
    pages: int
    word_count: int
    char_count: int

class ConfigureRequest(BaseModel):
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 4
    temperature: float = 0.0
    llm_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"

class ConfigureResponse(BaseModel):
    chunks_indexed: int
    embedding_model: str
    chunk_size: int
    top_k: int

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    question: str
    answer: str
    source_chunks: list[str]
    timestamp: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or TXT policy document. Returns session_id for subsequent calls."""
    content = await file.read()
    filename = file.filename or "document"
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext == "pdf":
        try:
            load_result = load_pdf_bytes(content, filename)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
    elif ext == "txt":
        load_result = load_txt_bytes(content, filename)
    else:
        raise HTTPException(status_code=422, detail="Only PDF and TXT files are supported.")
    sid = create_session()
    session = require_session(sid)
    session.load_result = load_result
    return {
        "session_id": sid,
        "filename": filename,
        "pages": load_result.pages,
        "word_count": load_result.word_count,
        "char_count": load_result.char_count,
    }


@router.post("/{session_id}/configure", response_model=ConfigureResponse)
def configure(session_id: str, req: ConfigureRequest):
    """Chunk the document and build the ChromaDB vector store."""
    session = _get_session(session_id)
    if session.load_result is None:
        raise HTTPException(status_code=400, detail="Upload a document first via POST /api/loan-rag/upload.")
    chunks = chunk_text(session.load_result, req.chunk_size, req.chunk_overlap)
    try:
        vs_result = build_vector_store(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector store build failed: {e}")
    session.vectorstore = vs_result.vectorstore
    session.rag_config = RAGConfig(
        llm_model=req.llm_model,
        chunk_size=req.chunk_size,
        chunk_overlap=req.chunk_overlap,
        top_k=req.top_k,
        temperature=req.temperature,
    )
    return {
        "chunks_indexed": vs_result.chunk_count,
        "embedding_model": vs_result.embedding_model,
        "chunk_size": req.chunk_size,
        "top_k": req.top_k,
    }


@router.post("/{session_id}/chat", response_model=ChatResponse)
def chat(session_id: str, req: ChatRequest):
    """Ask a question against the indexed document. Requires /configure first."""
    session = _get_session(session_id)
    if session.vectorstore is None or session.rag_config is None:
        raise HTTPException(status_code=400, detail="Call /configure first.")
    try:
        result = run_rag_query(req.question, session.vectorstore, session.rag_config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")
    entry = {
        "question": result.query,
        "answer": result.answer,
        "source_chunks": result.source_chunks,
        "timestamp": result.timestamp,
    }
    session.rag_history.append(entry)
    return entry


@router.get("/{session_id}/history")
def get_history(session_id: str):
    """Return the full chat history for this session."""
    session = _get_session(session_id)
    return session.rag_history


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_session(session_id: str) -> Session:
    try:
        return require_session(session_id)
    except SessionNotFound:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found. Call POST /api/loan-rag/upload first.",
        )
