import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    title: str,
    notification_type: str,
    message: str | None = None,
    related_to: str | None = None,
    related_record_id: uuid.UUID | None = None,
):
    """Internal helper - called from other services (lead, opportunity,
    activity) when a notification-worthy event happens. Does NOT
    commit - caller's existing transaction handles that, so the
    notification is saved atomically with the triggering change."""
    notification = Notification(
        tenant_id=tenant_id,
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_to=related_to,
        related_record_id=related_record_id,
    )
    db.add(notification)


async def list_notifications(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, unread_only: bool = False
) -> tuple[list[Notification], int]:
    query = select(Notification).where(Notification.tenant_id == tenant_id, Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.is_read == False)

    unread_count_query = select(func.count()).select_from(
        select(Notification).where(
            Notification.tenant_id == tenant_id, Notification.user_id == user_id, Notification.is_read == False
        ).subquery()
    )
    unread_count = (await db.execute(unread_count_query)).scalar_one()

    query = query.order_by(Notification.created_at.desc()).limit(50)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, unread_count


async def mark_as_read(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, notification_id: uuid.UUID) -> Notification | None:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id, Notification.tenant_id == tenant_id, Notification.user_id == user_id
        )
    )
    notification = result.scalar_one_or_none()
    if notification is None:
        return None
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_all_as_read(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(Notification).where(
            Notification.tenant_id == tenant_id, Notification.user_id == user_id, Notification.is_read == False
        )
    )
    notifications = result.scalars().all()
    for n in notifications:
        n.is_read = True
    await db.commit()
    return len(notifications)