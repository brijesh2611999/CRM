import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HSCodeBase(BaseModel):
    code: str
    name: str  # holds Description, per our earlier decision
    duty_rate_pct: float | None = None
    gst_rate_pct: float | None = None
    status: str = "Active"


class HSCodeCreate(HSCodeBase):
    pass


class HSCodeUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    duty_rate_pct: float | None = None
    gst_rate_pct: float | None = None
    status: str | None = None


class HSCodeRead(HSCodeBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None