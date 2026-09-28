"""
Role-Based Access Control (RBAC) and multi-tenancy enforcement.

Prevents unauthorized data leakage by filtering chunks before LLM exposure.
Implements defense-in-depth: check ACLs at retrieval time AND before generation.
"""

from app.models.schemas import Chunk, User


def filter_authorized_chunks(chunks: list[Chunk], user: User) -> list[Chunk]:
    """
    Filter chunks to only those the user is authorized to see.

    Rules:
        1. Chunk must belong to user's tenant (tenant_id must match)
        2. If chunk has allowed_roles, user must have at least one matching role
        3. If chunk has no allowed_roles, assume it's public within tenant

    This is a second ACL check (first one happens at retrieval time based on
    metadata filters). Defense-in-depth ensures no authorization bypass.

    Args:
        chunks: List of chunks retrieved from vector store
        user: Authenticated user with tenant and roles

    Returns:
        List of chunks the user is authorized to access
    """
    authorized = []
    for chunk in chunks:
        # Tenant isolation: user can only see their own tenant's data
        if chunk.tenant_id != user.tenant_id:
            continue

        # Role-based filtering: check if user has required role
        if chunk.allowed_roles:
            # If ACL is defined, user must have at least one matching role
            if not set(user.roles).intersection(chunk.allowed_roles):
                continue

        # All checks passed
        authorized.append(chunk)

    return authorized


def build_tenant_filter(tenant_id: str) -> dict:
    """
    Build a metadata filter for the vector store to limit retrieval to a tenant.

    This pre-filters results at retrieval time (first ACL check).

    Args:
        tenant_id: Tenant ID to filter by

    Returns:
        Filter dict compatible with LangChain retrievers
        Example: {"where": {"tenant_id": tenant_id}}
    """
    return {"tenant_id": tenant_id}
