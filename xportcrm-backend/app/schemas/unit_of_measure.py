import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UnitOfMeasureBase(BaseModel):
    code: str
    name: str
    category: str
    decimal_precision: int | None = None
    status: str = "Active"


class UnitOfMeasureCreate(UnitOfMeasureBase):
    pass


class UnitOfMeasureUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    category: str | None = None
    decimal_precision: int | None = None
    status: str | None = None


class UnitOfMeasureRead(UnitOfMeasureBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None