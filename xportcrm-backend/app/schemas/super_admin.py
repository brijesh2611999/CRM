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