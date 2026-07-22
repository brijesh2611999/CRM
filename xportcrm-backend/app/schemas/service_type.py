import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ServiceTypeBase(BaseModel):
    code: str
    name: str
    category: str
    description: str | None = None
    status: str = "Active"


class ServiceTypeCreate(ServiceTypeBase):
    pass


class ServiceTypeUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    category: str | None = None
    description: str | None = None
    status: str | None = None


class ServiceTypeRead(ServiceTypeBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None