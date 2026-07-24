import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    related_to: str
    related_record_id: uuid.UUID
    document_type: str | None = None
    original_filename: str
    content_type: str | None = None
    file_size_bytes: int
    uploaded_by: uuid.UUID | None = None
    created_at: datetime


class DocumentDownloadResponse(BaseModel):
    download_url: str
    filename: str