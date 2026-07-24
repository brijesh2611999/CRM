import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field_permission import FieldPermission


async def get_field_visibility_map(
    db: AsyncSession, tenant_id: uuid.UUID, role_id: uuid.UUID | None, module: str
) -> dict[str, str]:
    """Returns {field_name: visibility} for all sensitive fields
    configured for this role+module. Fields not present in the result
    are treated as 'Editable' (fully visible, no restriction) by default."""
    if role_id is None:
        return {}

    result = await db.execute(
        select(FieldPermission).where(
            FieldPermission.tenant_id == tenant_id,
            FieldPermission.role_id == role_id,
            FieldPermission.module == module,
        )
    )
    return {fp.field_name: fp.visibility for fp in result.scalars().all()}


def apply_field_visibility(record_dict: dict, visibility_map: dict[str, str]) -> dict:
    """Removes 'Hidden' fields entirely from the response dict.
    'ReadOnly' fields remain visible in output (read-only only matters
    for write operations, not display) - so no change needed there
    for GET responses. 'Editable' or unlisted fields are untouched."""
    result = dict(record_dict)
    for field_name, visibility in visibility_map.items():
        if visibility == "Hidden" and field_name in result:
            result.pop(field_name)
    return result


def strip_readonly_fields(update_dict: dict, visibility_map: dict[str, str]) -> dict:
    """For write operations (create/update): removes any field the
    role has marked 'ReadOnly' or 'Hidden' from the incoming update
    payload, so the user cannot change it even if they include it in
    the request body."""
    result = dict(update_dict)
    for field_name, visibility in visibility_map.items():
        if visibility in ("Hidden", "ReadOnly") and field_name in result:
            result.pop(field_name)
    return result