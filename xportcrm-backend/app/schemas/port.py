import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PortBase(BaseModel):
    code: str
    name: str
    city: str
    state: str | None = None
    country: str
    port_type: str
    unlocode: str | None = None
    status: str = "Active"


class PortCreate(PortBase):
    pass


class PortUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    port_type: str | None = None
    unlocode: str | None = None
    status: str | None = None


class PortRead(PortBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None