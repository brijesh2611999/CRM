import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ChargeHeadBase(BaseModel):
    code: str
    name: str
    category: str
    is_taxable: bool = False
    status: str = "Active"


class ChargeHeadCreate(ChargeHeadBase):
    pass


class ChargeHeadUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    category: str | None = None
    is_taxable: bool | None = None
    status: str | None = None


class ChargeHeadRead(ChargeHeadBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None