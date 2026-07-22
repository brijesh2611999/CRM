import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentTypeBase(BaseModel):
    code: str
    name: str
    module: str
    is_mandatory: bool = False
    status: str = "Active"


class DocumentTypeCreate(DocumentTypeBase):
    pass


class DocumentTypeUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    module: str | None = None
    is_mandatory: bool | None = None
    status: str | None = None


class DocumentTypeRead(DocumentTypeBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None