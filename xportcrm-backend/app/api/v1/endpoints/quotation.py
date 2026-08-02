import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id, get_current_user_id
from app.db.session import get_db
from app.schemas.quotation import (
    QuotationCreate, QuotationUpdate, QuotationRead,
    ChargeLineCreate, ChargeLineUpdate, ChargeLineRead,
)
from app.services import quotation_service
from app.api.deps import get_current_tenant_id, get_current_user_id, require_permission
from app.services.field_permission_service import get_field_visibility_map, apply_field_visibility
from app.services.export_service import export_to_csv, export_to_excel, serialize_for_export
from app.api.deps import get_current_user
from app.schemas.auth import CurrentUser

router = APIRouter()


@router.get("/", response_model=list[QuotationRead])
async def list_quotations(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await quotation_service.list_quotations(db, tenant_id)


@router.get("/export/csv")
async def export_quotations_csv(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items = await quotation_service.list_quotations(db, tenant_id)
    rows = serialize_for_export(items)
    return export_to_csv(rows, "quotations_export")


@router.get("/export/excel")
async def export_quotations_excel(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items = await quotation_service.list_quotations(db, tenant_id)
    rows = serialize_for_export(items)
    return export_to_excel(rows, "quotations_export")


# @router.post("/", response_model=QuotationRead, status_code=201)
# async def create_quotation(
#     data: QuotationCreate,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     user_id: uuid.UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await quotation_service.create_quotation(db, tenant_id, user_id, data)
@router.post("/", response_model=QuotationRead, status_code=201)
async def create_quotation(
    data: QuotationCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(require_permission("quotations", "create")),
):
    return await quotation_service.create_quotation(db, tenant_id, user_id, data)


# @router.get("/{quotation_id}", response_model=QuotationRead)
# async def get_quotation(
#     quotation_id: uuid.UUID,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     quotation = await quotation_service.get_quotation(db, tenant_id, quotation_id)
#     if quotation is None:
#         raise HTTPException(status_code=404, detail="Quotation not found")
#     return quotation
@router.get("/{quotation_id}", response_model=QuotationRead)
async def get_quotation(
    quotation_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    quotation = await quotation_service.get_quotation(db, current_user.tenant_id, quotation_id)
    if quotation is None:
        raise HTTPException(status_code=404, detail="Quotation not found")

    visibility_map = await get_field_visibility_map(db, current_user.tenant_id, current_user.role_id, "quotations")
    if not visibility_map:
        return quotation

    quote_dict = QuotationRead.model_validate(quotation).model_dump()
    return apply_field_visibility(quote_dict, visibility_map)

# @router.put("/{quotation_id}", response_model=QuotationRead)
# async def update_quotation(
#     quotation_id: uuid.UUID,
#     data: QuotationUpdate,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     user_id: uuid.UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     quotation = await quotation_service.update_quotation(db, tenant_id, user_id, quotation_id, data)
#     if quotation is None:
#         raise HTTPException(status_code=404, detail="Quotation not found")
#     return quotation
@router.put("/{quotation_id}", response_model=QuotationRead)
async def update_quotation(
    quotation_id: uuid.UUID,
    data: QuotationUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(require_permission("quotations", "update")),
):
    quotation = await quotation_service.update_quotation(db, tenant_id, user_id, quotation_id, data)
    if quotation is None:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation

# @router.delete("/{quotation_id}", response_model=QuotationRead)
# async def delete_quotation(
#     quotation_id: uuid.UUID,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     user_id: uuid.UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     quotation = await quotation_service.delete_quotation(db, tenant_id, user_id, quotation_id)
#     if quotation is None:
#         raise HTTPException(status_code=404, detail="Quotation not found")
#     return quotation
@router.delete("/{quotation_id}", response_model=QuotationRead)
async def delete_quotation(
    quotation_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(require_permission("quotations", "delete")),
):
    quotation = await quotation_service.delete_quotation(db, tenant_id, user_id, quotation_id)
    if quotation is None:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation

@router.post("/{quotation_id}/revise", response_model=QuotationRead)
async def create_revision(
    quotation_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    revision = await quotation_service.create_revision(db, tenant_id, user_id, quotation_id)
    if revision is None:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return revision


@router.get("/{quotation_id}/charge-lines", response_model=list[ChargeLineRead])
async def list_charge_lines(
    quotation_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await quotation_service.list_charge_lines(db, tenant_id, quotation_id)


@router.post("/{quotation_id}/charge-lines", response_model=ChargeLineRead, status_code=201)
async def add_charge_line(
    quotation_id: uuid.UUID,
    data: ChargeLineCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await quotation_service.add_charge_line(db, tenant_id, user_id, quotation_id, data)


@router.put("/{quotation_id}/charge-lines/{line_id}", response_model=ChargeLineRead)
async def update_charge_line(
    quotation_id: uuid.UUID,
    line_id: uuid.UUID,
    data: ChargeLineUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    line = await quotation_service.update_charge_line(db, tenant_id, user_id, quotation_id, line_id, data)
    if line is None:
        raise HTTPException(status_code=404, detail="Charge line not found")
    return line


@router.delete("/{quotation_id}/charge-lines/{line_id}", status_code=204)
async def delete_charge_line(
    quotation_id: uuid.UUID,
    line_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    deleted = await quotation_service.delete_charge_line(db, tenant_id, quotation_id, line_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Charge line not found")