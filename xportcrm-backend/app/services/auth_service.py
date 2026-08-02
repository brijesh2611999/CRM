import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.schemas.auth import TenantSignup, Login
from app.services.permission_service import seed_default_permissions


async def signup_tenant(db: AsyncSession, data: TenantSignup) -> str:
    tenant = Tenant(id=uuid.uuid4(), name=data.tenant_name, is_active=True)
    db.add(tenant)
    await db.flush()

    admin_role = Role(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Tenant Admin",
        code="TENANT_ADMIN",
        is_system_role=True,
        is_active=True,
        data_scope="All",  # Tenant Admin sees everything
    )
    db.add(admin_role)

    default_roles_info = [
        ("Sales Manager", "SALES_MANAGER", "Team"),
        ("Sales Executive", "SALES_EXECUTIVE", "Own"),
        ("Finance", "FINANCE", "All"),
        ("Customer Portal", "CUSTOMER_PORTAL", "Own"),
    ]

    roles_to_seed = [(admin_role, "TENANT_ADMIN")]

    for r_name, r_code, r_scope in default_roles_info:
        r = Role(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            name=r_name,
            code=r_code,
            is_system_role=True,
            is_active=True,
            data_scope=r_scope,
        )
        db.add(r)
        roles_to_seed.append((r, r_code))

    await db.flush()

    for role_obj, role_code in roles_to_seed:
        await seed_default_permissions(db, tenant.id, role_obj.id, role_code)

    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        role_id=admin_role.id,
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return create_access_token({
        "sub": str(user.id),
        "tenant_id": str(tenant.id),
        "role_id": str(admin_role.id),
        "email": user.email,
        "data_scope": admin_role.data_scope,
    })


async def login(db: AsyncSession, data: Login) -> str | None:
    result = await db.execute(select(User).where(User.email == data.email, User.is_active == True))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(data.password, user.hashed_password):
        return None

    data_scope = "Own"
    if user.role_id:
        role_result = await db.execute(select(Role).where(Role.id == user.role_id))
        role = role_result.scalar_one_or_none()
        if role:
            data_scope = role.data_scope

    return create_access_token({
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "role_id": str(user.role_id) if user.role_id else None,
        "email": user.email,
        "data_scope": data_scope,
    })