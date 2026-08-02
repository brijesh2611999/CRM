import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class SuperAdminLogin(BaseModel):
    email: EmailStr
    password: str


class SuperAdminToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SuperAdminCurrentUser(BaseModel):
    super_admin_id: uuid.UUID
    email: str


class TenantSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    is_active: bool
    created_at: datetime


class TenantStatusUpdate(BaseModel):
    is_active: bool


class DashboardMetrics(BaseModel):
    total_tenants: int
    active_tenants: int
    suspended_tenants: int
    total_users: int


class UserSummary(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    is_active: bool
    role_name: str | None


class TenantDetailResponse(BaseModel):
    tenant: TenantSummary
    users: list[UserSummary]