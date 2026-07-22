import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id, get_current_user_id
from app.db.session import get_db
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunityRead
from app.services import opportunity_service
from app.schemas.common import PaginatedResponse
from app.services.export_service import export_to_csv, export_to_excel, serialize_for_export
from app.schemas.common import BulkAssignRequest, BulkStatusChangeRequest, BulkIdsRequest, BulkActionResult
from app.api.deps import get_current_tenant_id, get_current_user_id, get_current_user
from app.schemas.auth import CurrentUser

router = APIRouter()


# @router.get("/", response_model=list[OpportunityRead])
# async def list_opportunities(
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await opportunity_service.list_opportunities(db, tenant_id)

@router.post("/bulk/change-stage", response_model=BulkActionResult)
async def bulk_change_stage(
    data: BulkStatusChangeRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    success_count, failed_ids = await opportunity_service.bulk_change_stage(db, tenant_id, user_id, data.ids, data.status)
    return BulkActionResult(success_count=success_count, failed_ids=failed_ids)


@router.post("/bulk/delete", response_model=BulkActionResult)
async def bulk_delete_opportunities(
    data: BulkIdsRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    success_count, failed_ids = await opportunity_service.bulk_delete_opportunities(db, tenant_id, user_id, data.ids)
    return BulkActionResult(success_count=success_count, failed_ids=failed_ids)

@router.get("/export/csv")
async def export_opportunities_csv(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items, _ = await opportunity_service.list_opportunities(db, tenant_id, page=1, page_size=100000)
    rows = serialize_for_export(items)
    return export_to_csv(rows, "opportunities_export")


@router.get("/export/excel")
async def export_opportunities_excel(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items, _ = await opportunity_service.list_opportunities(db, tenant_id, page=1, page_size=100000)
    rows = serialize_for_export(items)
    return export_to_excel(rows, "opportunities_export")

# @router.get("/", response_model=PaginatedResponse[OpportunityRead])
# async def list_opportunities(
#     search: str | None = None,
#     stage: str | None = None,
#     opportunity_type: str | None = None,
#     assigned_to_id: uuid.UUID | None = None,
#     account_id: uuid.UUID | None = None,
#     page: int = 1,
#     page_size: int = 20,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     items, total = await opportunity_service.list_opportunities(
#         db, tenant_id, search, stage, opportunity_type, assigned_to_id, account_id, page, page_size
#     )
#     return PaginatedResponse(total=total, page=page, page_size=page_size, items=items)
@router.get("/", response_model=PaginatedResponse[OpportunityRead])
async def list_opportunities(
    search: str | None = None,
    stage: str | None = None,
    opportunity_type: str | None = None,
    assigned_to_id: uuid.UUID | None = None,
    account_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await opportunity_service.list_opportunities(
        db, current_user.tenant_id, current_user.user_id, current_user.data_scope,
        search, stage, opportunity_type, assigned_to_id, account_id, page, page_size
    )
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items)


@router.post("/", response_model=OpportunityRead, status_code=201)
async def create_opportunity(
    data: OpportunityCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await opportunity_service.create_opportunity(db, tenant_id, user_id, data)


@router.get("/{opportunity_id}", response_model=OpportunityRead)
async def get_opportunity(
    opportunity_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    opportunity = await opportunity_service.get_opportunity(db, tenant_id, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@router.put("/{opportunity_id}", response_model=OpportunityRead)
async def update_opportunity(
    opportunity_id: uuid.UUID,
    data: OpportunityUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    opportunity = await opportunity_service.update_opportunity(db, tenant_id, user_id, opportunity_id, data)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@router.delete("/{opportunity_id}", response_model=OpportunityRead)
async def delete_opportunity(
    opportunity_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    opportunity = await opportunity_service.delete_opportunity(db, tenant_id, user_id, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity



@router.post("/bulk/assign", response_model=BulkActionResult)
async def bulk_assign_opportunities(
    data: BulkAssignRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    success_count, failed_ids = await opportunity_service.bulk_assign_opportunities(db, tenant_id, user_id, data.ids, data.assigned_to_id)
    return BulkActionResult(success_count=success_count, failed_ids=failed_ids)

