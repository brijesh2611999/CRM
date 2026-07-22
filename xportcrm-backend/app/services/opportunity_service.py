import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, STAGE_PROBABILITY_MAP
from sqlalchemy import select, func


# async def list_opportunities(db: AsyncSession, tenant_id: uuid.UUID) -> list[Opportunity]:
#     result = await db.execute(
#         select(Opportunity).where(Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False)
#     )
#     return result.scalars().all()
# async def list_opportunities(
#     db: AsyncSession,
#     tenant_id: uuid.UUID,
#     search: str | None = None,
#     stage: str | None = None,
#     opportunity_type: str | None = None,
#     assigned_to_id: uuid.UUID | None = None,
#     account_id: uuid.UUID | None = None,
#     page: int = 1,
#     page_size: int = 20,
# ) -> tuple[list[Opportunity], int]:
#     query = select(Opportunity).where(Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False)

#     if search:
#         pattern = f"%{search}%"
#         query = query.where(Opportunity.opportunity_name.ilike(pattern))
#     if stage:
#         query = query.where(Opportunity.stage == stage)
#     if opportunity_type:
#         query = query.where(Opportunity.opportunity_type == opportunity_type)
#     if assigned_to_id:
#         query = query.where(Opportunity.assigned_to_id == assigned_to_id)
#     if account_id:
#         query = query.where(Opportunity.account_id == account_id)

#     count_query = select(func.count()).select_from(query.subquery())
#     total = (await db.execute(count_query)).scalar_one()

#     query = query.order_by(Opportunity.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
#     result = await db.execute(query)
#     items = result.scalars().all()

#     return items, total

async def list_opportunities(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    current_user_id: uuid.UUID,
    data_scope: str = "Own",
    search: str | None = None,
    stage: str | None = None,
    opportunity_type: str | None = None,
    assigned_to_id: uuid.UUID | None = None,
    account_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Opportunity], int]:
    query = select(Opportunity).where(Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False)

    if data_scope == "Own":
        query = query.where(
            (Opportunity.assigned_to_id == current_user_id) | (Opportunity.created_by == current_user_id)
        )

    if search:
        pattern = f"%{search}%"
        query = query.where(Opportunity.opportunity_name.ilike(pattern))
    if stage:
        query = query.where(Opportunity.stage == stage)
    if opportunity_type:
        query = query.where(Opportunity.opportunity_type == opportunity_type)
    if assigned_to_id:
        query = query.where(Opportunity.assigned_to_id == assigned_to_id)
    if account_id:
        query = query.where(Opportunity.account_id == account_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Opportunity.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, total

async def get_opportunity(db: AsyncSession, tenant_id: uuid.UUID, opportunity_id: uuid.UUID) -> Opportunity | None:
    result = await db.execute(
        select(Opportunity).where(
            Opportunity.id == opportunity_id, Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


def _apply_stage_probability(data: dict) -> dict:
    if data.get("probability_pct") is None and data.get("stage") in STAGE_PROBABILITY_MAP:
        data["probability_pct"] = STAGE_PROBABILITY_MAP[data["stage"]]
    return data


async def create_opportunity(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: OpportunityCreate) -> Opportunity:
    payload = _apply_stage_probability(data.model_dump())
    opportunity = Opportunity(tenant_id=tenant_id, created_by=user_id, **payload)
    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)
    return opportunity


async def update_opportunity(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, opportunity_id: uuid.UUID, data: OpportunityUpdate
) -> Opportunity | None:
    opportunity = await get_opportunity(db, tenant_id, opportunity_id)
    if opportunity is None:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "stage" in update_data and "probability_pct" not in update_data:
        update_data["probability_pct"] = STAGE_PROBABILITY_MAP.get(update_data["stage"], opportunity.probability_pct)

    for field, value in update_data.items():
        setattr(opportunity, field, value)
    opportunity.modified_by = user_id

    await db.commit()
    await db.refresh(opportunity)
    return opportunity


async def delete_opportunity(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, opportunity_id: uuid.UUID) -> Opportunity | None:
    opportunity = await get_opportunity(db, tenant_id, opportunity_id)
    if opportunity is None:
        return None
    opportunity.is_deleted = True
    opportunity.modified_by = user_id
    await db.commit()
    await db.refresh(opportunity)
    return opportunity


async def bulk_assign_opportunities(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, ids: list[uuid.UUID], assigned_to_id: uuid.UUID
) -> tuple[int, list[uuid.UUID]]:
    success_count = 0
    failed_ids = []
    for opp_id in ids:
        opp = await get_opportunity(db, tenant_id, opp_id)
        if opp is None:
            failed_ids.append(opp_id)
            continue
        opp.assigned_to_id = assigned_to_id
        opp.modified_by = user_id
        success_count += 1
    await db.commit()
    return success_count, failed_ids


async def bulk_change_stage(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, ids: list[uuid.UUID], stage: str
) -> tuple[int, list[uuid.UUID]]:
    """Also auto-updates probability_pct per stage, matching single-record update behavior."""
    success_count = 0
    failed_ids = []
    for opp_id in ids:
        opp = await get_opportunity(db, tenant_id, opp_id)
        if opp is None:
            failed_ids.append(opp_id)
            continue
        opp.stage = stage
        opp.probability_pct = STAGE_PROBABILITY_MAP.get(stage, opp.probability_pct)
        opp.modified_by = user_id
        success_count += 1
    await db.commit()
    return success_count, failed_ids


async def bulk_delete_opportunities(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, ids: list[uuid.UUID]
) -> tuple[int, list[uuid.UUID]]:
    success_count = 0
    failed_ids = []
    for opp_id in ids:
        opp = await get_opportunity(db, tenant_id, opp_id)
        if opp is None:
            failed_ids.append(opp_id)
            continue
        opp.is_deleted = True
        opp.modified_by = user_id
        success_count += 1
    await db.commit()
    return success_count, failed_ids