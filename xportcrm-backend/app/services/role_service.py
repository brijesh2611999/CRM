import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate, PermissionItem
from app.models.field_permission import FieldPermission
from app.schemas.role import FieldPermissionItem


def _generate_role_code(name: str) -> str:
    """Turns 'Regional Sales Lead' into 'REGIONAL_SALES_LEAD'."""
    return re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")


async def list_roles(db: AsyncSession, tenant_id: uuid.UUID) -> list[Role]:
    from sqlalchemy import or_
    result = await db.execute(
        select(Role).where(
            or_(Role.tenant_id == tenant_id, Role.tenant_id.is_(None))
        )
    )
    return result.scalars().all()


async def get_role(db: AsyncSession, tenant_id: uuid.UUID, role_id: uuid.UUID) -> Role | None:
    from sqlalchemy import or_
    result = await db.execute(
        select(Role).where(
            Role.id == role_id,
            or_(Role.tenant_id == tenant_id, Role.tenant_id.is_(None))
        )
    )
    return result.scalar_one_or_none()


async def create_role(db: AsyncSession, tenant_id: uuid.UUID | None, data: RoleCreate, is_system: bool = False) -> Role:
    """XPO-41 AC-01: Tenant Admin can create unlimited custom roles.
    New custom roles start with NO permissions (all modules/actions
    denied) - admin must explicitly grant permissions afterward via
    set_permissions()."""
    role = Role(
        tenant_id=tenant_id,
        name=data.name,
        code=_generate_role_code(data.name),
        is_system_role=is_system,
        is_active=data.is_active,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update_role(db: AsyncSession, tenant_id: uuid.UUID | None, role_id: uuid.UUID, data: RoleUpdate, is_super_admin: bool = False) -> Role | None:
    role = await get_role(db, tenant_id, role_id)
    if role is None:
        return None
    if role.is_system_role and not is_super_admin:
        raise HTTPException(status_code=400, detail="System roles cannot be modified")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(role, field, value)
    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, tenant_id: uuid.UUID | None, role_id: uuid.UUID, is_super_admin: bool = False) -> Role | None:
    role = await get_role(db, tenant_id, role_id)
    if role is None:
        return None
    if role.is_system_role and not is_super_admin:
        raise HTTPException(status_code=400, detail="System roles cannot be deleted")
    role.is_active = False
    await db.commit()
    await db.refresh(role)
    return role


async def clone_role(db: AsyncSession, tenant_id: uuid.UUID, source_role_id: uuid.UUID, new_name: str) -> Role | None:
    """XPO-41 AC-02: Role cloning copies complete permission structure."""
    source = await get_role(db, tenant_id, source_role_id)
    if source is None:
        return None

    new_role = Role(
        tenant_id=tenant_id,
        name=new_name,
        code=_generate_role_code(new_name),
        is_system_role=False,
        is_active=True,
    )
    db.add(new_role)
    await db.flush()

    result = await db.execute(select(Permission).where(Permission.tenant_id == tenant_id, Permission.role_id == source_role_id))
    source_permissions = result.scalars().all()

    for perm in source_permissions:
        db.add(Permission(
            tenant_id=tenant_id,
            role_id=new_role.id,
            module=perm.module,
            action=perm.action,
            allowed=perm.allowed,
        ))

    await db.commit()
    await db.refresh(new_role)
    return new_role


async def get_permissions(db: AsyncSession, tenant_id: uuid.UUID | None, role_id: uuid.UUID) -> list[Permission]:
    from sqlalchemy import or_
    result = await db.execute(
        select(Permission).where(
            Permission.role_id == role_id,
            or_(Permission.tenant_id == tenant_id, Permission.tenant_id.is_(None))
        )
    )
    return result.scalars().all()


async def set_permissions(
    db: AsyncSession, tenant_id: uuid.UUID | None, role_id: uuid.UUID, permissions: list[PermissionItem], is_super_admin: bool = False
) -> list[Permission]:
    """Upserts permission rows for a role - for each (module, action)
    pair given, create it if missing or update 'allowed' if it exists."""
    role = await get_role(db, tenant_id, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.is_system_role and not is_super_admin:
        raise HTTPException(status_code=400, detail="System role permissions cannot be modified")

    for item in permissions:
        result = await db.execute(
            select(Permission).where(
                Permission.tenant_id == tenant_id,
                Permission.role_id == role_id,
                Permission.module == item.module,
                Permission.action == item.action,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.allowed = item.allowed
        else:
            db.add(Permission(
                tenant_id=tenant_id,
                role_id=role_id,
                module=item.module,
                action=item.action,
                allowed=item.allowed,
            ))

    await db.commit()
    return await get_permissions(db, tenant_id, role_id)


async def assign_user_to_role(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, role_id: uuid.UUID) -> User | None:
    role = await get_role(db, tenant_id, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    result = await db.execute(select(User).where(User.id == user_id, User.tenant_id == tenant_id))
    user = result.scalar_one_or_none()
    if user is None:
        return None

    user.role_id = role_id
    await db.commit()
    await db.refresh(user)
    return user


async def set_field_permissions(
    db: AsyncSession, tenant_id: uuid.UUID | None, role_id: uuid.UUID, field_permissions: list[FieldPermissionItem], is_super_admin: bool = False
) -> list[FieldPermission]:
    role = await get_role(db, tenant_id, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.is_system_role and not is_super_admin:
        raise HTTPException(status_code=400, detail="System role permissions cannot be modified")

    for item in field_permissions:
        result = await db.execute(
            select(FieldPermission).where(
                FieldPermission.tenant_id == tenant_id,
                FieldPermission.role_id == role_id,
                FieldPermission.module == item.module,
                FieldPermission.field_name == item.field_name,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.visibility = item.visibility
        else:
            db.add(FieldPermission(
                tenant_id=tenant_id, role_id=role_id, module=item.module,
                field_name=item.field_name, visibility=item.visibility,
            ))

    await db.commit()

    result = await db.execute(
        select(FieldPermission).where(FieldPermission.tenant_id == tenant_id, FieldPermission.role_id == role_id)
    )
    return result.scalars().all()