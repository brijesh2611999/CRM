import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id, get_current_user_id
from app.db.session import get_db
from app.schemas.account import AccountCreate, AccountUpdate, AccountRead
from app.services import account_service
from app.schemas.common import PaginatedResponse
from app.services.export_service import export_to_csv, export_to_excel, serialize_for_export
from app.api.deps import get_current_tenant_id, get_current_user_id, require_permission
from app.services.field_permission_service import get_field_visibility_map, apply_field_visibility, strip_readonly_fields
from app.api.deps import get_current_user
from app.schemas.auth import CurrentUser


router = APIRouter()


# @router.get("/", response_model=list[AccountRead])
# async def list_accounts(
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await account_service.list_accounts(db, tenant_id)


@router.get("/export/csv")
async def export_accounts_csv(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items, _ = await account_service.list_accounts(db, tenant_id, page=1, page_size=100000)
    rows = serialize_for_export(items)
    return export_to_csv(rows, "accounts_export")


@router.get("/export/excel")
async def export_accounts_excel(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    items, _ = await account_service.list_accounts(db, tenant_id, page=1, page_size=100000)
    rows = serialize_for_export(items)
    return export_to_excel(rows, "accounts_export")

# @router.get("/", response_model=PaginatedResponse[AccountRead])
# async def list_accounts(
#     search: str | None = None,
#     account_type: str | None = None,
#     status: str | None = None,
#     kyc_status: str | None = None,
#     page: int = 1,
#     page_size: int = 25,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     items, total = await account_service.list_accounts(
#         db, tenant_id, search, account_type, status, kyc_status, page, page_size
#     )
#     return PaginatedResponse(total=total, page=page, page_size=page_size, items=items)
@router.get("/", response_model=list[AccountRead])
async def list_accounts(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await account_service.list_accounts(db, current_user.tenant_id, page=1, page_size=10000)
    visibility_map = await get_field_visibility_map(db, current_user.tenant_id, current_user.role_id, "accounts")
    if not visibility_map:
        return items
    # Apply field hiding (credit_limit, annual_revenue_potential, etc.)
    filtered = []
    for acc in items:
        acc_dict = AccountRead.model_validate(acc).model_dump()
        filtered.append(apply_field_visibility(acc_dict, visibility_map))
    return filtered
# @router.post("/", response_model=AccountRead, status_code=201)
# async def create_account(
#     data: AccountCreate,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     user_id: uuid.UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await account_service.create_account(db, tenant_id, user_id, data)
@router.post("/", response_model=AccountRead, status_code=201)
async def create_account(
    data: AccountCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(require_permission("accounts", "create")),
):
    return await account_service.create_account(db, tenant_id, user_id, data)


# @router.get("/{account_id}", response_model=AccountRead)
# async def get_account(
#     account_id: uuid.UUID,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     account = await account_service.get_account(db, tenant_id, account_id)
#     if account is None:
#         raise HTTPException(status_code=404, detail="Account not found")
#     return account
@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = await account_service.get_account(db, current_user.tenant_id, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    visibility_map = await get_field_visibility_map(db, current_user.tenant_id, current_user.role_id, "accounts")
    if not visibility_map:
        return account

    acc_dict = AccountRead.model_validate(account).model_dump()
    return apply_field_visibility(acc_dict, visibility_map)

# @router.put("/{account_id}", response_model=AccountRead)
# async def update_account(
#     account_id: uuid.UUID,
#     data: AccountUpdate,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     user_id: uuid.UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     account = await account_service.update_account(db, tenant_id, user_id, account_id, data)
#     if account is None:
#         raise HTTPException(status_code=404, detail="Account not found")
#     return account
# @router.put("/{account_id}", response_model=AccountRead)
# async def update_account(
#     account_id: uuid.UUID,
#     data: AccountUpdate,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     user_id: uuid.UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
#     _current_user = Depends(require_permission("accounts", "update")),
# ):
#     account = await account_service.update_account(db, tenant_id, user_id, account_id, data)
#     if account is None:
#         raise HTTPException(status_code=404, detail="Account not found")
#     return account
@router.put("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: uuid.UUID,
    data: AccountUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(require_permission("accounts", "update")),
):
    visibility_map = await get_field_visibility_map(db, current_user.tenant_id, current_user.role_id, "accounts")
    update_dict = strip_readonly_fields(data.model_dump(exclude_unset=True), visibility_map)

    account = await account_service.update_account(db, current_user.tenant_id, current_user.user_id, account_id, AccountUpdate(**update_dict))
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# @router.delete("/{account_id}", response_model=AccountRead)
# async def deactivate_account(
#     account_id: uuid.UUID,
#     tenant_id: uuid.UUID = Depends(get_current_tenant_id),
#     user_id: uuid.UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     account = await account_service.deactivate_account(db, tenant_id, user_id, account_id)
#     if account is None:
#         raise HTTPException(status_code=404, detail="Account not found")
#     return account
@router.delete("/{account_id}", response_model=AccountRead)
async def deactivate_account(
    account_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(require_permission("accounts", "delete")),
):
    account = await account_service.deactivate_account(db, tenant_id, user_id, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.post("/{primary_id}/merge/{duplicate_id}", response_model=AccountRead)
async def merge_accounts(
    primary_id: uuid.UUID,
    duplicate_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    account = await account_service.merge_accounts(db, tenant_id, user_id, primary_id, duplicate_id)
    if account is None:
        raise HTTPException(status_code=404, detail="One or both accounts not found")
    return account

