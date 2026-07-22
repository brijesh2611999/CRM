import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role


# Matches XPO-41 "Standard Permission Matrix" table.
# Format: role_code -> module -> set of allowed actions.
DEFAULT_PERMISSION_MATRIX = {
    "TENANT_ADMIN": {
        "dashboards": {"create", "read", "update", "delete", "approve", "export"},
        "leads": {"create", "read", "update", "delete", "approve", "export"},
        "contacts": {"create", "read", "update", "delete", "approve", "export"},
        "accounts": {"create", "read", "update", "delete", "approve", "export"},
        "opportunities": {"create", "read", "update", "delete", "approve", "export"},
        "quotations": {"create", "read", "update", "delete", "approve", "export"},
        "activities": {"create", "read", "update", "delete", "approve", "export"},
        "masters": {"create", "read", "update", "delete", "approve", "export"},
        "reports": {"create", "read", "update", "delete", "approve", "export"},
        "settings": {"create", "read", "update", "delete", "approve", "export"},
    },
    "SALES_MANAGER": {
        "dashboards": {"create", "read", "update", "delete", "approve", "export"},
        "leads": {"create", "read", "update", "delete", "approve", "export"},
        "contacts": {"create", "read", "update", "delete", "approve", "export"},
        "accounts": {"create", "read", "update", "delete", "approve", "export"},
        "opportunities": {"create", "read", "update", "delete", "approve", "export"},
        "quotations": {"create", "read", "update", "delete", "approve", "export"},
        "activities": {"create", "read", "update", "delete", "approve", "export"},
        "masters": {"read"},
        "reports": {"read", "export"},
        "settings": {"read"},
    },
    "SALES_EXECUTIVE": {
        "dashboards": {"read"},
        "leads": {"create", "read", "update", "delete"},
        "contacts": {"create", "read", "update", "delete"},
        "accounts": {"create", "read", "update", "delete"},
        "opportunities": {"create", "read", "update", "delete"},
        "quotations": {"create", "read", "update", "delete"},
        "activities": {"create", "read", "update", "delete"},
        "masters": {"read"},
        "reports": {"read", "export"},
        "settings": set(),
    },
    "FINANCE": {
        "dashboards": {"read"},
        "leads": set(),
        "contacts": set(),
        "accounts": {"read"},
        "opportunities": set(),
        "quotations": {"read"},
        "activities": {"create", "read", "update", "delete", "export"},
        "masters": {"read"},
        "reports": {"read", "export"},
        "settings": set(),
    },
    "CUSTOMER_PORTAL": {
        "dashboards": set(),
        "leads": set(),
        "contacts": set(),
        "accounts": {"read"},
        "opportunities": set(),
        "quotations": {"read"},
        "activities": set(),
        "masters": set(),
        "reports": set(),
        "settings": set(),
    },
}


async def seed_default_permissions(db: AsyncSession, tenant_id: uuid.UUID, role_id: uuid.UUID, role_code: str):
    """Creates Permission rows for a role based on the standard matrix
    (XPO-41). Called right after a Role is created (e.g. during
    tenant signup, or when an admin creates a new role from a
    standard template)."""
    matrix = DEFAULT_PERMISSION_MATRIX.get(role_code, {})
    permissions = []
    for module, actions in matrix.items():
        for action in ["create", "read", "update", "delete", "approve", "export"]:
            permissions.append(
                Permission(
                    tenant_id=tenant_id,
                    role_id=role_id,
                    module=module,
                    action=action,
                    allowed=action in actions,
                )
            )
    db.add_all(permissions)
    await db.flush()


async def has_permission(db: AsyncSession, tenant_id: uuid.UUID, role_id: uuid.UUID | None, module: str, action: str) -> bool:
    """Core permission check: does this role have 'action' allowed on 'module'?"""
    if role_id is None:
        return False

    result = await db.execute(
        select(Permission).where(
            Permission.tenant_id == tenant_id,
            Permission.role_id == role_id,
            Permission.module == module,
            Permission.action == action,
            Permission.allowed == True,
        )
    )
    return result.scalar_one_or_none() is not None