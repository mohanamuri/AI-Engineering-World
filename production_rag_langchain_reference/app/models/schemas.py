"""
Pydantic schemas for request/response validation.

These are the same as the scratch version to maintain API compatibility.
"""

from pydantic import BaseModel, Field


class User(BaseModel):
    """User identity and authorization context."""
    user_id: str
    tenant_id: str
    roles: list[str] = Field(default_factory=list)


class Chunk(BaseModel):
    """A text chunk from a document, with metadata and ACLs."""
    id: str
    document_id: str
    tenant_id: str
    text: str
    source: str
    title: str
    chunk_index: int
    allowed_roles: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Result of a retrieval operation."""
    chunk: Chunk
    score: float
    retrieval_method: str


class AskRequest(BaseModel):
    """User query request."""
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=8, ge=1, le=20)


class Citation(BaseModel):
    """Citation of a source document."""
    chunk_id: str
    title: str
    source: str


class AskResponse(BaseModel):
    """Response containing answer and citations."""
    answer: str
    citations: list[Citation]
    cached: bool = False
    trace_id: str
