import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class QuoteTncTemplateBase(BaseModel):
    code: str
    name: str
    terms_and_conditions: str
    is_default: bool = False
    status: str = "Active"


class QuoteTncTemplateCreate(QuoteTncTemplateBase):
    pass


class QuoteTncTemplateUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    terms_and_conditions: str | None = None
    is_default: bool | None = None
    status: str | None = None


class QuoteTncTemplateRead(QuoteTncTemplateBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None