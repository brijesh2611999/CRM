import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Document(Base):
    """Generic file attachment - can attach to any record type (Account
    KYC docs, Quotation attachments, Lead documents, etc.) via the
    same related_to/related_record_id polymorphic pattern used by
    Activity. Physical files are stored in Azure Blob Storage;
    blob_name is the unique path within the container."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    related_to: Mapped[str] = mapped_column(String(20), nullable=False)  # Account/Lead/Quote/Contact etc.
    related_record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    document_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. 'PAN', 'GSTIN', 'Rate Card'
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    blob_name: Mapped[str] = mapped_column(String(500), nullable=False)  # path within Azure container
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())