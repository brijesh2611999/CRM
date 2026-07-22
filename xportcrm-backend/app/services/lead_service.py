import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.lead import Lead
from app.models.account import Account
from app.schemas.lead import LeadCreate, LeadUpdate
from sqlalchemy import select, func  # for pagination and search filter
from app.models.opportunity import Opportunity
from app.schemas.lead import ConvertToOpportunityRequest

# without pagination 
# async def list_leads(db: AsyncSession, tenant_id: uuid.UUID) -> list[Lead]:
#     result = await db.execute(
#         select(Lead).where(Lead.tenant_id == tenant_id, Lead.is_deleted == False)
#     )
#     return result.scalars().all()
# async def list_leads(
#     db: AsyncSession,
#     tenant_id: uuid.UUID,
#     search: str | None = None,
#     lead_status: str | None = None,
#     lead_source: str | None = None,
#     lead_temperature: str | None = None,
#     assigned_to_id: uuid.UUID | None = None,
#     page: int = 1,
#     page_size: int = 25,
# ) -> tuple[list[Lead], int]:
#     """Returns (items, total_count). Supports:
#     - search: partial match on Company Name or Contact Person (XPO-44 section 5)
#     - lead_status, lead_source, lead_temperature, assigned_to_id: filters (section 6)
#     - page/page_size: pagination (section 4A)
#     """
#     query = select(Lead).where(Lead.tenant_id == tenant_id, Lead.is_deleted == False)
    
#     if search:
#         pattern = f"%{search}%"
#         query = query.where(
#             (Lead.company_name.ilike(pattern)) | (Lead.contact_person.ilike(pattern))
#         )
#     if lead_status:
#         query = query.where(Lead.lead_status == lead_status)
#     if lead_source:
#         query = query.where(Lead.lead_source == lead_source)
#     if lead_temperature:
#         query = query.where(Lead.lead_temperature == lead_temperature)
#     if assigned_to_id:
#         query = query.where(Lead.assigned_to_id == assigned_to_id)

#     count_query = select(func.count()).select_from(query.subquery())
#     total = (await db.execute(count_query)).scalar_one()

#     query = query.order_by(Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
#     result = await db.execute(query)
#     items = result.scalars().all()

#     return items, total
async def list_leads(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    current_user_id: uuid.UUID,
    data_scope: str = "Own",
    search: str | None = None,
    lead_status: str | None = None,
    lead_source: str | None = None,
    lead_temperature: str | None = None,
    assigned_to_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 25,
) -> tuple[list[Lead], int]:
    query = select(Lead).where(Lead.tenant_id == tenant_id, Lead.is_deleted == False)

    # XPO-41 Data Access Security: "Own Records" scope restricts results
    # to leads assigned to (or created by) the current user. "Team" and
    # "Branch" scopes are treated as "All" for now, since Team/Branch
    # structures haven't been built yet - flagged as a deferred gap.
    if data_scope == "Own":
        query = query.where(
            (Lead.assigned_to_id == current_user_id) | (Lead.created_by == current_user_id)
        )

    if search:
        pattern = f"%{search}%"
        query = query.where(
            (Lead.company_name.ilike(pattern)) | (Lead.contact_person.ilike(pattern))
        )
    if lead_status:
        query = query.where(Lead.lead_status == lead_status)
    if lead_source:
        query = query.where(Lead.lead_source == lead_source)
    if lead_temperature:
        query = query.where(Lead.lead_temperature == lead_temperature)
    if assigned_to_id:
        query = query.where(Lead.assigned_to_id == assigned_to_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, total


async def get_lead(db: AsyncSession, tenant_id: uuid.UUID, lead_id: uuid.UUID) -> Lead | None:
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id, Lead.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def _warn_duplicate(db: AsyncSession, tenant_id: uuid.UUID, company_name: str, email: str | None) -> bool:
    if not email:
        return False
    result = await db.execute(
        select(Lead).where(
            Lead.tenant_id == tenant_id,
            Lead.company_name == company_name,
            Lead.email == email,
            Lead.is_deleted == False,
        )
    )
    return result.scalar_one_or_none() is not None


async def create_lead(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: LeadCreate) -> tuple[Lead, bool]:
    is_duplicate = await _warn_duplicate(db, tenant_id, data.company_name, data.email)
    lead = Lead(tenant_id=tenant_id, created_by=user_id, **data.model_dump())
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead, is_duplicate


async def update_lead(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, lead_id: uuid.UUID, data: LeadUpdate) -> Lead | None:
    lead = await get_lead(db, tenant_id, lead_id)
    if lead is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    lead.modified_by = user_id
    await db.commit()
    await db.refresh(lead)
    return lead


async def delete_lead(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, lead_id: uuid.UUID) -> Lead | None:
    lead = await get_lead(db, tenant_id, lead_id)
    if lead is None:
        return None
    lead.is_deleted = True
    lead.modified_by = user_id
    await db.commit()
    await db.refresh(lead)
    return lead


async def convert_lead_to_account(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, lead_id: uuid.UUID) -> Lead | None:
    lead = await get_lead(db, tenant_id, lead_id)
    if lead is None:
        return None

    if lead.converted_account_id is not None:
        raise HTTPException(status_code=400, detail="Lead has already been converted to an Account")

    account = Account(
        tenant_id=tenant_id,
        created_by=user_id,
        code=f"ACC-{str(uuid.uuid4())[:8].upper()}",
        name=lead.company_name,
        account_type="Shipper",
        country=lead.origin_region or "Unknown",
        primary_contact_name=lead.contact_person,
        primary_contact_email=lead.email or "unknown@placeholder.com",
        primary_contact_phone=lead.phone or lead.mobile,
        key_commodities=lead.commodity_type,
        assigned_account_manager_id=lead.assigned_to_id,
    )
    db.add(account)
    await db.flush()

    lead.converted_account_id = account.id
    lead.lead_status = "Qualified"
    lead.modified_by = user_id

    await db.commit()
    await db.refresh(lead)
    return lead


async def convert_lead_to_opportunity(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, lead_id: uuid.UUID, data: ConvertToOpportunityRequest
) -> Lead | None:
    """XPO-44 section 13: Convert Lead -> Opportunity.
    Requires the Lead to already have a converted_account_id (i.e.
    must be converted to an Account first) - since Opportunity
    requires a linked Account per XPO-47's schema. If not yet
    converted, we auto-convert to Account first, then create the
    Opportunity on top of it."""
    lead = await get_lead(db, tenant_id, lead_id)
    if lead is None:
        return None

    if lead.converted_to_opportunity:
        raise HTTPException(status_code=400, detail="Lead has already been converted to an Opportunity")

    # If not yet converted to an Account, do that first (reusing existing logic)
    if lead.converted_account_id is None:
        lead = await convert_lead_to_account(db, tenant_id, user_id, lead_id)

    opportunity = Opportunity(
        tenant_id=tenant_id,
        created_by=user_id,
        opportunity_name=data.opportunity_name,
        account_id=lead.converted_account_id,
        opportunity_type=data.opportunity_type,
        stage="Discovery",
        estimated_amount=data.estimated_amount,
        expected_close_date=data.expected_close_date,
        probability_pct=10,  # matches Discovery stage default (XPO-47)
        origin=lead.origin_region,
        destination=lead.destination_region,
        commodity=lead.commodity_type,
        assigned_to_id=lead.assigned_to_id or user_id,
    )
    db.add(opportunity)
    await db.flush()

    lead.converted_to_opportunity = True
    lead.modified_by = user_id

    await db.commit()
    await db.refresh(lead)
    return lead



async def bulk_assign_leads(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, lead_ids: list[uuid.UUID], assigned_to_id: uuid.UUID
) -> tuple[int, list[uuid.UUID]]:
    success_count = 0
    failed_ids = []
    for lead_id in lead_ids:
        lead = await get_lead(db, tenant_id, lead_id)
        if lead is None:
            failed_ids.append(lead_id)
            continue
        lead.assigned_to_id = assigned_to_id
        lead.modified_by = user_id
        success_count += 1
    await db.commit()
    return success_count, failed_ids


async def bulk_change_status(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, lead_ids: list[uuid.UUID], status: str
) -> tuple[int, list[uuid.UUID]]:
    success_count = 0
    failed_ids = []
    for lead_id in lead_ids:
        lead = await get_lead(db, tenant_id, lead_id)
        if lead is None:
            failed_ids.append(lead_id)
            continue
        lead.lead_status = status
        lead.modified_by = user_id
        success_count += 1
    await db.commit()
    return success_count, failed_ids


async def bulk_delete_leads(
    db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, lead_ids: list[uuid.UUID]
) -> tuple[int, list[uuid.UUID]]:
    success_count = 0
    failed_ids = []
    for lead_id in lead_ids:
        lead = await get_lead(db, tenant_id, lead_id)
        if lead is None:
            failed_ids.append(lead_id)
            continue
        lead.is_deleted = True
        lead.modified_by = user_id
        success_count += 1
    await db.commit()
    return success_count, failed_ids