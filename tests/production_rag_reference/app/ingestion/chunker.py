from app.models.schemas import Chunk
import uuid

def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    """Simple word chunker. Production systems often use heading/semantic-aware chunks."""
    words = text.split()
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks

def build_chunks(doc, tenant_id, allowed_roles, chunk_size, overlap):
    parts = chunk_text(doc["text"], chunk_size, overlap)
    document_id = str(uuid.uuid4())
    return [
        Chunk(
            id=str(uuid.uuid4()),
            document_id=document_id,
            tenant_id=tenant_id,
            text=part,
            source=doc["source"],
            title=doc["title"],
            chunk_index=i,
            allowed_roles=allowed_roles,
        )
        for i, part in enumerate(parts)
    ]
