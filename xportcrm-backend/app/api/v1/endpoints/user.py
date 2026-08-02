import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id
from app.db.session import get_db
from app.schemas.user import UserRead, UserCreate
from app.services import user_service

router = APIRouter()


@router.get("/", response_model=list[UserRead])
async def list_users(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.list_users(db, tenant_id)

@router.post("/", response_model=UserRead)
async def create_user(
    user_data: UserCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.create_user(db, tenant_id, user_data)
