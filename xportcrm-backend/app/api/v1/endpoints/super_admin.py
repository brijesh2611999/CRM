import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_super_admin
from app.db.session import get_db
from app.schemas.super_admin import (
    SuperAdminLogin, SuperAdminToken, TenantSummary, TenantStatusUpdate, SuperAdminCurrentUser, DashboardMetrics
)
from app.services import super_admin_service

router = APIRouter()


@router.post("/login", response_model=SuperAdminToken)
async def login(data: SuperAdminLogin, db: AsyncSession = Depends(get_db)):
    token = await super_admin_service.login(db, data)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return SuperAdminToken(access_token=token)


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    return await super_admin_service.get_dashboard_metrics(db)


@router.get("/tenants", response_model=list[TenantSummary])
async def list_tenants(
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    return await super_admin_service.list_tenants(db)


from app.schemas.super_admin import (
    SuperAdminLogin, SuperAdminToken, TenantSummary, TenantStatusUpdate, SuperAdminCurrentUser, DashboardMetrics, TenantDetailResponse
)

@router.get("/tenants/{tenant_id}/details", response_model=TenantDetailResponse)
async def get_tenant_details(
    tenant_id: uuid.UUID,
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    tenant = await super_admin_service.get_tenant_details(db, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.post("/tenants/{tenant_id}/impersonate")
async def impersonate_tenant(
    tenant_id: uuid.UUID,
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    token = await super_admin_service.impersonate_tenant(db, tenant_id)
    if token is None:
        raise HTTPException(status_code=404, detail="No active users found in this tenant to impersonate")
    return {"access_token": token, "token_type": "bearer"}


@router.put("/tenants/{tenant_id}/status", response_model=TenantSummary)
async def set_tenant_status(
    tenant_id: uuid.UUID,
    data: TenantStatusUpdate,
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    tenant = await super_admin_service.set_tenant_status(db, tenant_id, data)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

from app.schemas.role import RoleCreate, RoleRead, RoleUpdate, PermissionItem, PermissionRead, FieldPermissionItem, FieldPermissionRead
from app.services import role_service

@router.get("/roles", response_model=list[RoleRead])
async def super_admin_list_roles(
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    return await role_service.list_roles(db, None)

@router.post("/roles", response_model=RoleRead)
async def super_admin_create_role(
    data: RoleCreate,
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    return await role_service.create_role(db, None, data, is_system=True)

@router.put("/roles/{role_id}", response_model=RoleRead)
async def super_admin_update_role(
    role_id: uuid.UUID,
    data: RoleUpdate,
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    role = await role_service.update_role(db, None, role_id, data, is_super_admin=True)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.delete("/roles/{role_id}", response_model=RoleRead)
async def super_admin_delete_role(
    role_id: uuid.UUID,
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    role = await role_service.delete_role(db, None, role_id, is_super_admin=True)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.get("/roles/{role_id}/permissions", response_model=list[PermissionRead])
async def super_admin_get_permissions(
    role_id: uuid.UUID,
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    return await role_service.get_permissions(db, None, role_id)

@router.put("/roles/{role_id}/permissions", response_model=list[PermissionRead])
async def super_admin_set_permissions(
    role_id: uuid.UUID,
    permissions: list[PermissionItem],
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    return await role_service.set_permissions(db, None, role_id, permissions, is_super_admin=True)

@router.put("/roles/{role_id}/field-permissions", response_model=list[FieldPermissionRead])
async def super_admin_set_field_permissions(
    role_id: uuid.UUID,
    field_permissions: list[FieldPermissionItem],
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    return await role_service.set_field_permissions(db, None, role_id, field_permissions, is_super_admin=True)