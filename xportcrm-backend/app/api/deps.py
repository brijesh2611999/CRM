import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.schemas.auth import CurrentUser
from app.db.session import get_db
from app.services.permission_service import has_permission
from app.schemas.super_admin import SuperAdminCurrentUser

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return CurrentUser(
        user_id=uuid.UUID(payload["sub"]),
        tenant_id=uuid.UUID(payload["tenant_id"]),
        role_id=uuid.UUID(payload["role_id"]) if payload.get("role_id") else None,
        email=payload["email"],
        data_scope=payload.get("data_scope", "Own"),
    )


def get_current_tenant_id(current_user: CurrentUser = Depends(get_current_user)) -> uuid.UUID:
    return current_user.tenant_id


def get_current_user_id(current_user: CurrentUser = Depends(get_current_user)) -> uuid.UUID:
    return current_user.user_id


def require_permission(module: str, action: str):
    async def checker(
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        allowed = await has_permission(db, current_user.tenant_id, current_user.role_id, module, action)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not permitted: {action} on {module}")
        return current_user

    return checker


def get_current_super_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> SuperAdminCurrentUser:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    if payload.get("scope") != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super Admin access required")

    return SuperAdminCurrentUser(
        super_admin_id=uuid.UUID(payload["sub"]),
        email=payload["email"],
    )