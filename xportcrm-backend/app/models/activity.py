from datetime import datetime
import uuid

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, AuditMixin, SoftDeleteMixin


class Activity(Base, UUIDPKMixin, TenantMixin, AuditMixin, SoftDeleteMixin):
    """Activity Module (XPO-48). Calls, meetings, emails, tasks, etc.
    linked to a Lead, Account, Opportunity, or Quote.

    related_to + related_record_id together point to one of those
    four record types (polymorphic association) - see note below on
    why there's no single DB-level foreign key here."""

    __tablename__ = "activities"

    activity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Call / Meeting / Email / Task / Note / WhatsApp / Demo / Site Visit

    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    related_to: Mapped[str] = mapped_column(String(20), nullable=False)
    # Lead / Account / Opportunity / Quote
    related_record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    assigned_to_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Pending")
    # Pending / Completed / Cancelled / Deferred

    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="Medium")
    # Low / Medium / High / Urgent

    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)

    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    follow_up_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)