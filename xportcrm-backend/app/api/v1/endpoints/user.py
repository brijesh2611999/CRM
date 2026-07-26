import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id
from app.db.session import get_db
from app.schemas.user import UserRead
from app.services import user_service

router = APIRouter()


@router.get("/", response_model=list[UserRead])
async def list_users(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.list_users(db, tenant_id)
