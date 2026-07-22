import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ActivityBase(BaseModel):
    activity_type: str
    subject: str
    description: str | None = None
    related_to: str  # Lead / Account / Opportunity / Quote
    related_record_id: uuid.UUID
    due_date: datetime | None = None
    completed_date: datetime | None = None
    assigned_to_id: uuid.UUID
    status: str = "Pending"
    priority: str = "Medium"
    outcome: str | None = None
    follow_up_required: bool = False
    follow_up_date: datetime | None = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    activity_type: str | None = None
    subject: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    completed_date: datetime | None = None
    assigned_to_id: uuid.UUID | None = None
    status: str | None = None
    priority: str | None = None
    outcome: str | None = None
    follow_up_required: bool | None = None
    follow_up_date: datetime | None = None


class ActivityRead(ActivityBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None