import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_id
from app.db.session import get_db
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleRead, PermissionRead,
    SetPermissionsRequest, AssignUserRoleRequest,
)
from app.services import role_service

router = APIRouter()


@router.get("/", response_model=list[RoleRead])
async def list_roles(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await role_service.list_roles(db, tenant_id)


@router.post("/", response_model=RoleRead, status_code=201)
async def create_role(
    data: RoleCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await role_service.create_role(db, tenant_id, data)


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    role = await role_service.get_role(db, tenant_id, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: uuid.UUID,
    data: RoleUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    role = await role_service.update_role(db, tenant_id, role_id, data)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.delete("/{role_id}", response_model=RoleRead)
async def delete_role(
    role_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    role = await role_service.delete_role(db, tenant_id, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/{role_id}/clone", response_model=RoleRead, status_code=201)
async def clone_role(
    role_id: uuid.UUID,
    new_name: str,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    role = await role_service.clone_role(db, tenant_id, role_id, new_name)
    if role is None:
        raise HTTPException(status_code=404, detail="Source role not found")
    return role


@router.get("/{role_id}/permissions", response_model=list[PermissionRead])
async def get_permissions(
    role_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await role_service.get_permissions(db, tenant_id, role_id)


@router.put("/{role_id}/permissions", response_model=list[PermissionRead])
async def set_permissions(
    role_id: uuid.UUID,
    data: SetPermissionsRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    return await role_service.set_permissions(db, tenant_id, role_id, data.permissions)


@router.post("/assign-user")
async def assign_user_to_role(
    data: AssignUserRoleRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    user = await role_service.assign_user_to_role(db, tenant_id, data.user_id, data.role_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User assigned to role successfully", "user_id": str(user.id), "role_id": str(user.role_id)}