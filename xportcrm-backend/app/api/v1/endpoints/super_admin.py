import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_super_admin
from app.db.session import get_db
from app.schemas.super_admin import (
    SuperAdminLogin, SuperAdminToken, TenantSummary, TenantStatusUpdate, SuperAdminCurrentUser,
)
from app.services import super_admin_service

router = APIRouter()


@router.post("/login", response_model=SuperAdminToken)
async def login(data: SuperAdminLogin, db: AsyncSession = Depends(get_db)):
    token = await super_admin_service.login(db, data)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return SuperAdminToken(access_token=token)


@router.get("/tenants", response_model=list[TenantSummary])
async def list_tenants(
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    return await super_admin_service.list_tenants(db)


@router.get("/tenants/{tenant_id}", response_model=TenantSummary)
async def get_tenant(
    tenant_id: uuid.UUID,
    current_admin: SuperAdminCurrentUser = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    tenant = await super_admin_service.get_tenant(db, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


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