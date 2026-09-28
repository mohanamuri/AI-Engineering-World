"""
Authentication and authorization using FastAPI dependencies.

Production systems should use OIDC/JWT with a trusted identity provider.
This is a demo implementation only.
"""

from fastapi import Header, HTTPException
from app.core.config import get_settings
from app.models.schemas import User


async def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
    x_roles: str | None = Header(default=None),
) -> User:
    """
    Extract user identity from request headers.

    Production Implementation:
        - Validate JWT/OIDC tokens from Authorization header
        - Verify token signature with trusted public key
        - Extract user_id, tenant_id, roles from signed claims
        - Never trust caller-supplied role headers

    Args:
        x_user_id: User ID (demo header)
        x_tenant_id: Tenant ID (demo header)
        x_roles: Comma-separated roles (demo header)

    Returns:
        User object with identity and roles

    Raises:
        HTTPException: If authentication is not configured
    """
    if get_settings().dev_auth_enabled:
        return User(
            user_id=x_user_id or "demo-user",
            tenant_id=x_tenant_id or "demo-tenant",
            roles=(x_roles or "employee").split(","),
        )
    raise HTTPException(status_code=401, detail="Authentication not configured")


def require_role(user: User, allowed: set[str]) -> None:
    """
    Check if user has one of the required roles.

    Args:
        user: User object from authentication
        allowed: Set of allowed role names

    Raises:
        HTTPException: If user does not have required role
    """
    if not set(user.roles).intersection(allowed):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
