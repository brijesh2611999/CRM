import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    is_active: bool

class UserRead(UserBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    role_id: uuid.UUID | None = None
    created_at: datetime
    modified_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
