 # common fields mixin (Code, Name, Status, audit)
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPKMixin:
    """Primary key as UUID - safer for multi-tenant SaaS than sequential ints
    (avoids leaking record counts / guessable IDs across tenants)."""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TenantMixin:
    """Every business table belongs to exactly one tenant.
    Enforces data isolation required by XPO-41 AC-10."""
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )


class AuditMixin:
    """Created/Modified by + date, required on every master (XPO-54 Common Fields)
    and every CRM record (audit trail requirement in XPO-44/45/46/47/48/49)."""
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )


class SoftDeleteMixin:
    """Soft delete only - records referenced in transactions cannot be
    permanently deleted (XPO-54 AC-08, XPO-47 'Soft Delete only')."""
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MasterFieldsMixin(AuditMixin, SoftDeleteMixin):
    """Common fields shared by ALL master tables per XPO-54:
    Code, Name, Status, Created By/Date, Modified By/Date.
    Individual masters (Port, Airport, Currency...) add their own
    specific fields on top of this."""
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Active")