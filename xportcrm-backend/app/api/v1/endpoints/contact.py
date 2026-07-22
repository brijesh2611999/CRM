import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id, get_current_user_id
from app.db.session import get_db
from app.schemas.contact import ContactCreate, ContactUpdate, ContactRead
from app.services import contact_service
from app.schemas.common import PaginatedResponse
from app.services.export_service import export_to_csv, export_to_excel, serialize_for_export


router = APIRouter()


# @router.get("/", response_model=list[ContactRead])
# async def list_contacts(
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await contact_service.list_contacts(db, tenant_id)

@router.get("/export/csv")
async def export_contacts_csv(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items, _ = await contact_service.list_contacts(db, tenant_id, page=1, page_size=100000)
    rows = serialize_for_export(items)
    return export_to_csv(rows, "contacts_export")


@router.get("/export/excel")
async def export_contacts_excel(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items, _ = await contact_service.list_contacts(db, tenant_id, page=1, page_size=100000)
    rows = serialize_for_export(items)
    return export_to_excel(rows, "contacts_export")

@router.get("/", response_model=PaginatedResponse[ContactRead])
async def list_contacts(
    search: str | None = None,
    account_id: uuid.UUID | None = None,
    role_type: str | None = None,
    is_primary_contact: bool | None = None,
    do_not_contact: bool | None = None,
    page: int = 1,
    page_size: int = 25,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items, total = await contact_service.list_contacts(
        db, tenant_id, search, account_id, role_type, is_primary_contact, do_not_contact, page, page_size
    )
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items)


@router.post("/", response_model=ContactRead, status_code=201)
async def create_contact(
    data: ContactCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await contact_service.create_contact(db, tenant_id, user_id, data)


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    contact_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    contact = await contact_service.get_contact(db, tenant_id, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: uuid.UUID,
    data: ContactUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    contact = await contact_service.update_contact(db, tenant_id, user_id, contact_id, data)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactRead)
async def delete_contact(
    contact_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    contact = await contact_service.delete_contact(db, tenant_id, user_id, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

