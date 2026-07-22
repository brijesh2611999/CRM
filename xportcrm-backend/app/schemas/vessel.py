import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class VesselBase(BaseModel):
    code: str
    name: str
    imo_number: str
    flag_country: str | None = None
    operator: str | None = None
    vessel_type: str | None = None
    status: str = "Active"


class VesselCreate(VesselBase):
    pass


class VesselUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    imo_number: str | None = None
    flag_country: str | None = None
    operator: str | None = None
    vessel_type: str | None = None
    status: str | None = None


class VesselRead(VesselBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None