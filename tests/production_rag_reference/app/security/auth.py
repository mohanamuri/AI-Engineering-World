from fastapi import Header, HTTPException
from app.core.config import get_settings
from app.models.schemas import User

async def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
    x_roles: str | None = Header(default=None),
) -> User:
    """
    Demo authentication only.

    Production: validate an OIDC/JWT token and derive identity, tenant and
    roles from trusted signed claims. Never trust caller-supplied role headers.
    """
    if get_settings().dev_auth_enabled:
        return User(
            user_id=x_user_id or "demo-user",
            tenant_id=x_tenant_id or "demo-tenant",
            roles=(x_roles or "employee").split(","),
        )
    raise HTTPException(status_code=401, detail="Authentication provider not configured")

def require_role(user: User, allowed: set[str]) -> None:
    if not set(user.roles).intersection(allowed):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
