import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ContainerTypeBase(BaseModel):
    code: str
    name: str
    teu_factor: float
    length_feet: float | None = None
    max_weight_kg: float | None = None
    status: str = "Active"


class ContainerTypeCreate(ContainerTypeBase):
    pass


class ContainerTypeUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    teu_factor: float | None = None
    length_feet: float | None = None
    max_weight_kg: float | None = None
    status: str | None = None


class ContainerTypeRead(ContainerTypeBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None