import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LeadSourceMasterBase(BaseModel):
    code: str
    name: str
    status: str = "Active"


class LeadSourceMasterCreate(LeadSourceMasterBase):
    pass


class LeadSourceMasterUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    status: str | None = None


class LeadSourceMasterRead(LeadSourceMasterBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None