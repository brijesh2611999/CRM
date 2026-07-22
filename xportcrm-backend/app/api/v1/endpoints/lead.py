import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id, get_current_user_id, require_permission
from app.db.session import get_db
from app.schemas.lead import LeadCreate, LeadUpdate, LeadRead
from app.services import lead_service
from app.schemas.common import PaginatedResponse
from app.schemas.lead import LeadCreate, LeadUpdate, LeadRead, ConvertToOpportunityRequest
from app.services.export_service import export_to_csv, export_to_excel, serialize_for_export
from app.models.lead import Lead
from app.schemas.common import BulkAssignRequest, BulkStatusChangeRequest, BulkIdsRequest, BulkActionResult
from app.api.deps import get_current_tenant_id, get_current_user_id, get_current_user, require_permission
from app.schemas.auth import CurrentUser


router = APIRouter()


# @router.get("/", response_model=list[LeadRead])
# async def list_leads(
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await lead_service.list_leads(db, tenant_id)

@router.post("/bulk/assign", response_model=BulkActionResult)
async def bulk_assign_leads(
    data: BulkAssignRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    success_count, failed_ids = await lead_service.bulk_assign_leads(db, tenant_id, user_id, data.ids, data.assigned_to_id)
    return BulkActionResult(success_count=success_count, failed_ids=failed_ids)


@router.post("/bulk/change-status", response_model=BulkActionResult)
async def bulk_change_status(
    data: BulkStatusChangeRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    success_count, failed_ids = await lead_service.bulk_change_status(db, tenant_id, user_id, data.ids, data.status)
    return BulkActionResult(success_count=success_count, failed_ids=failed_ids)


@router.post("/bulk/delete", response_model=BulkActionResult)
async def bulk_delete_leads(
    data: BulkIdsRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    success_count, failed_ids = await lead_service.bulk_delete_leads(db, tenant_id, user_id, data.ids)
    return BulkActionResult(success_count=success_count, failed_ids=failed_ids)


@router.get("/export/csv")
async def export_leads_csv(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items, _ = await lead_service.list_leads(db, tenant_id, page=1, page_size=100000)
    rows = serialize_for_export(items)
    return export_to_csv(rows, "leads_export")


@router.get("/export/excel")
async def export_leads_excel(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items, _ = await lead_service.list_leads(db, tenant_id, page=1, page_size=100000)
    rows = serialize_for_export(items)
    return export_to_excel(rows, "leads_export")

# @router.get("/", response_model=PaginatedResponse[LeadRead])
# async def list_leads(
#     search: str | None = None,
#     lead_status: str | None = None,
#     lead_source: str | None = None,
#     lead_temperature: str | None = None,
#     assigned_to_id: uuid.UUID | None = None,
#     page: int = 1,
#     page_size: int = 25,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     items, total = await lead_service.list_leads(
#         db, tenant_id, search, lead_status, lead_source, lead_temperature, assigned_to_id, page, page_size
#     )
#     return PaginatedResponse(total=total, page=page, page_size=page_size, items=items)
@router.get("/", response_model=PaginatedResponse[LeadRead])
async def list_leads(
    search: str | None = None,
    lead_status: str | None = None,
    lead_source: str | None = None,
    lead_temperature: str | None = None,
    assigned_to_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 25,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await lead_service.list_leads(
        db, current_user.tenant_id, current_user.user_id, current_user.data_scope,
        search, lead_status, lead_source, lead_temperature, assigned_to_id, page, page_size
    )
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items)


@router.post("/", response_model=LeadRead, status_code=201)
async def create_lead(
    data: LeadCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    lead, is_duplicate = await lead_service.create_lead(db, tenant_id, user_id, data)
    return lead


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(
    lead_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    lead = await lead_service.get_lead(db, tenant_id, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadRead)
async def update_lead(
    lead_id: uuid.UUID,
    data: LeadUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    lead = await lead_service.update_lead(db, tenant_id, user_id, lead_id, data)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.delete("/{lead_id}", response_model=LeadRead)
async def delete_lead(
    lead_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(require_permission("leads", "delete")),
):
    lead = await lead_service.delete_lead(db, tenant_id, user_id, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/{lead_id}/convert-to-account", response_model=LeadRead)
async def convert_lead_to_account(
    lead_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    lead = await lead_service.convert_lead_to_account(db, tenant_id, user_id, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/{lead_id}/convert-to-opportunity", response_model=LeadRead)
async def convert_lead_to_opportunity(
    lead_id: uuid.UUID,
    data: ConvertToOpportunityRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    lead = await lead_service.convert_lead_to_opportunity(db, tenant_id, user_id, lead_id, data)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

