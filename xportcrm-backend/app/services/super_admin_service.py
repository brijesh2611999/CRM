import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_super_admin_token, create_access_token
from app.models.super_admin import SuperAdmin
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.schemas.super_admin import SuperAdminLogin, TenantStatusUpdate, DashboardMetrics, TenantDetailResponse, UserSummary
from sqlalchemy import func


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


async def get_dashboard_metrics(db: AsyncSession) -> DashboardMetrics:
    total_tenants = await db.scalar(select(func.count(Tenant.id)))
    active_tenants = await db.scalar(select(func.count(Tenant.id)).where(Tenant.is_active == True))
    suspended_tenants = total_tenants - (active_tenants or 0) if total_tenants else 0
    total_users = await db.scalar(select(func.count(User.id)))

    return DashboardMetrics(
        total_tenants=total_tenants or 0,
        active_tenants=active_tenants or 0,
        suspended_tenants=suspended_tenants,
        total_users=total_users or 0
    )


async def get_tenant_details(db: AsyncSession, tenant_id: uuid.UUID) -> TenantDetailResponse | None:
    tenant = await get_tenant(db, tenant_id)
    if tenant is None:
        return None
    
    result = await db.execute(
        select(User, Role.name)
        .outerjoin(Role, User.role_id == Role.id)
        .where(User.tenant_id == tenant_id)
    )
    rows = result.all()
    
    users = []
    for user, role_name in rows:
        users.append(UserSummary(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            is_active=user.is_active,
            role_name=role_name
        ))
        
    return TenantDetailResponse(
        tenant=tenant,
        users=users
    )


async def impersonate_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> str | None:
    # Find the earliest created active user for this tenant (usually the admin who signed up)
    result = await db.execute(
        select(User)
        .where(User.tenant_id == tenant_id, User.is_active == True)
        .order_by(User.created_at.asc())
        .limit(1)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        return None
        
    return create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "tenant_id": str(user.tenant_id),
        "role_id": str(user.role_id) if user.role_id else "",
    })