import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class IndustryTypeBase(BaseModel):
    code: str
    name: str
    status: str = "Active"


class IndustryTypeCreate(IndustryTypeBase):
    pass


class IndustryTypeUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    status: str | None = None


class IndustryTypeRead(IndustryTypeBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None