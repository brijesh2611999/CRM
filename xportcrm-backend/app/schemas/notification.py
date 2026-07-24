import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    message: str | None = None
    notification_type: str
    related_to: str | None = None
    related_record_id: uuid.UUID | None = None
    is_read: bool
    created_at: datetime