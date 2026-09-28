from app.models.schemas import Chunk, User

def can_read_chunk(user: User, chunk: Chunk) -> bool:
    # Tenant isolation must be enforced at retrieval/data layer in production.
    if chunk.tenant_id != user.tenant_id:
        return False
    if not chunk.allowed_roles:
        return True
    return bool(set(chunk.allowed_roles) & set(user.roles))

def filter_authorized_chunks(chunks: list[Chunk], user: User) -> list[Chunk]:
    return [c for c in chunks if can_read_chunk(user, c)]
