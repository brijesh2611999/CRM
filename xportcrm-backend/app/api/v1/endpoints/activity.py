import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id, get_current_user_id
from app.db.session import get_db
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityRead
from app.services import activity_service

router = APIRouter()


@router.get("/", response_model=list[ActivityRead])
async def list_activities(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await activity_service.list_activities(db, tenant_id)


@router.post("/", response_model=ActivityRead, status_code=201)
async def create_activity(
    data: ActivityCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await activity_service.create_activity(db, tenant_id, user_id, data)


@router.get("/{activity_id}", response_model=ActivityRead)
async def get_activity(
    activity_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    activity = await activity_service.get_activity(db, tenant_id, activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.put("/{activity_id}", response_model=ActivityRead)
async def update_activity(
    activity_id: uuid.UUID,
    data: ActivityUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    activity = await activity_service.update_activity(db, tenant_id, user_id, activity_id, data)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.delete("/{activity_id}", response_model=ActivityRead)
async def delete_activity(
    activity_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    activity = await activity_service.delete_activity(db, tenant_id, user_id, activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.get("/timeline/{related_to}/{related_record_id}", response_model=list[ActivityRead])
async def get_timeline(
    related_to: str,
    related_record_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await activity_service.get_timeline_for_record(db, tenant_id, related_to, related_record_id)