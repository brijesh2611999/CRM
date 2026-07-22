import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    name: str
    is_active: bool = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class RoleRead(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    code: str
    is_system_role: bool
    created_at: datetime
    modified_at: datetime | None = None


class PermissionItem(BaseModel):
    module: str
    action: str
    allowed: bool


class PermissionRead(PermissionItem):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class SetPermissionsRequest(BaseModel):
    permissions: list[PermissionItem]


class AssignUserRoleRequest(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID