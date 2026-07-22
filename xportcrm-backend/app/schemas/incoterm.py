import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class IncotermBase(BaseModel):
    code: str
    name: str
    responsibility_summary: str | None = None
    status: str = "Active"


class IncotermCreate(IncotermBase):
    pass


class IncotermUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    responsibility_summary: str | None = None
    status: str | None = None


class IncotermRead(IncotermBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None