import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.activity import Activity
from app.models.lead import Lead
from app.models.account import Account
from app.models.opportunity import Opportunity
from app.models.quotation import Quotation
from app.schemas.activity import ActivityCreate, ActivityUpdate

RELATED_TO_MODELS = {
    "Lead": Lead,
    "Account": Account,
    "Opportunity": Opportunity,
    "Quote": Quotation,
}


async def _validate_related_record(db: AsyncSession, tenant_id: uuid.UUID, related_to: str, related_record_id: uuid.UUID):
    model = RELATED_TO_MODELS.get(related_to)
    if model is None:
        raise HTTPException(status_code=400, detail=f"Invalid related_to value: {related_to}")

    result = await db.execute(
        select(model).where(model.id == related_record_id, model.tenant_id == tenant_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=400, detail=f"{related_to} record not found for the given related_record_id")


async def list_activities(db: AsyncSession, tenant_id: uuid.UUID) -> list[Activity]:
    result = await db.execute(
        select(Activity).where(Activity.tenant_id == tenant_id, Activity.is_deleted == False)
    )
    return result.scalars().all()


async def get_activity(db: AsyncSession, tenant_id: uuid.UUID, activity_id: uuid.UUID) -> Activity | None:
    result = await db.execute(
        select(Activity).where(
            Activity.id == activity_id, Activity.tenant_id == tenant_id, Activity.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def create_activity(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: ActivityCreate) -> Activity:
    await _validate_related_record(db, tenant_id, data.related_to, data.related_record_id)

    activity = Activity(tenant_id=tenant_id, created_by=user_id, **data.model_dump())
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def update_activity(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, activity_id: uuid.UUID, data: ActivityUpdate
) -> Activity | None:
    activity = await get_activity(db, tenant_id, activity_id)
    if activity is None:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if update_data.get("status") == "Completed" and activity.completed_date is None:
        update_data["completed_date"] = datetime.now(timezone.utc)

    follow_up_required = update_data.get("follow_up_required", activity.follow_up_required)
    follow_up_date = update_data.get("follow_up_date", activity.follow_up_date)
    if follow_up_required and follow_up_date is None:
        raise HTTPException(status_code=400, detail="Follow-up Date is required when Follow-up Required is Yes")

    for field, value in update_data.items():
        setattr(activity, field, value)
    activity.modified_by = user_id

    await db.commit()
    await db.refresh(activity)
    return activity


async def delete_activity(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, activity_id: uuid.UUID) -> Activity | None:
    activity = await get_activity(db, tenant_id, activity_id)
    if activity is None:
        return None
    activity.is_deleted = True
    activity.modified_by = user_id
    await db.commit()
    await db.refresh(activity)
    return activity


async def get_timeline_for_record(
    db: AsyncSession, tenant_id: uuid.UUID, related_to: str, related_record_id: uuid.UUID
) -> list[Activity]:
    result = await db.execute(
        select(Activity)
        .where(
            Activity.tenant_id == tenant_id,
            Activity.related_to == related_to,
            Activity.related_record_id == related_record_id,
            Activity.is_deleted == False,
        )
        .order_by(Activity.created_at.desc())
    )
    return result.scalars().all()