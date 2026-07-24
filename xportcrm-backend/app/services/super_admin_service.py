import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_super_admin_token
from app.models.super_admin import SuperAdmin
from app.models.tenant import Tenant
from app.schemas.super_admin import SuperAdminLogin, TenantStatusUpdate


async def login(db: AsyncSession, data: SuperAdminLogin) -> str | None:
    result = await db.execute(select(SuperAdmin).where(SuperAdmin.email == data.email, SuperAdmin.is_active == True))
    admin = result.scalar_one_or_none()

    if admin is None or not verify_password(data.password, admin.hashed_password):
        return None

    return create_super_admin_token({"sub": str(admin.id), "email": admin.email})


async def list_tenants(db: AsyncSession) -> list[Tenant]:
    result = await db.execute(select(Tenant))
    return result.scalars().all()


async def get_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant | None:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    return result.scalar_one_or_none()


async def set_tenant_status(db: AsyncSession, tenant_id: uuid.UUID, data: TenantStatusUpdate) -> Tenant | None:
    """Suspend/reactivate a tenant - e.g. for non-payment (billing not
    modeled yet, but the on/off switch is here)."""
    tenant = await get_tenant(db, tenant_id)
    if tenant is None:
        return None
    tenant.is_active = data.is_active
    await db.commit()
    await db.refresh(tenant)
    return tenant