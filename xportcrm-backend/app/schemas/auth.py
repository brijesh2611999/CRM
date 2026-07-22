import uuid
from pydantic import BaseModel, EmailStr


class TenantSignup(BaseModel):
    """Creates a brand new Tenant + its first (admin) User together -
    this is how a new company signs up for the SaaS."""

    tenant_name: str
    full_name: str
    email: EmailStr
    password: str


class Login(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    """What we extract from a decoded JWT - used throughout the app
    instead of the old X-Tenant-Id header hack."""

    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role_id: uuid.UUID | None = None
    email: str
    data_scope: str = "Own"