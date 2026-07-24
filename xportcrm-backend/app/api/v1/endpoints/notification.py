import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id, get_current_user_id
from app.db.session import get_db
from app.schemas.notification import NotificationRead
from app.services import notification_service

router = APIRouter()


@router.get("/")
async def list_notifications(
    unread_only: bool = False,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    items, unread_count = await notification_service.list_notifications(db, tenant_id, user_id, unread_only)
    return {
        "unread_count": unread_count,
        "notifications": [NotificationRead.model_validate(n) for n in items],
    }


@router.put("/{notification_id}/read", response_model=NotificationRead)
async def mark_as_read(
    notification_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    notification = await notification_service.mark_as_read(db, tenant_id, user_id, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.put("/read-all")
async def mark_all_as_read(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    count = await notification_service.mark_all_as_read(db, tenant_id, user_id)
    return {"message": f"{count} notifications marked as read"}