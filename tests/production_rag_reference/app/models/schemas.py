from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: str
    tenant_id: str
    roles: list[str] = Field(default_factory=list)

class Chunk(BaseModel):
    id: str
    document_id: str
    tenant_id: str
    text: str
    source: str
    title: str
    chunk_index: int
    allowed_roles: list[str] = Field(default_factory=list)

class SearchResult(BaseModel):
    chunk: Chunk
    score: float
    retrieval_method: str

class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=8, ge=1, le=20)

class Citation(BaseModel):
    chunk_id: str
    title: str
    source: str

class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    cached: bool = False
    trace_id: str
