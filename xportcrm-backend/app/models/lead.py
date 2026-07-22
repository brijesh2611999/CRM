from datetime import datetime
import uuid

from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, AuditMixin, SoftDeleteMixin


class Lead(Base, UUIDPKMixin, TenantMixin, AuditMixin, SoftDeleteMixin):
    """Leads Module (XPO-44). Entry point of the CRM sales pipeline."""

    __tablename__ = "leads"

    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_person: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(15), nullable=True)

    lead_source: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # Website / Referral / Trade Show / Cold Call / Email Campaign / Partner / LinkedIn / Exhibition

    lead_status: Mapped[str] = mapped_column(String(20), nullable=False, default="New")
    # New / Contacted / Qualified / Unqualified / Lost

    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    service_interest: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Multi-select stored as comma-separated, per our earlier tags decision (Option A)

    origin_region: Mapped[str | None] = mapped_column(String(150), nullable=True)
    destination_region: Mapped[str | None] = mapped_column(String(150), nullable=True)
    estimated_monthly_volume: Mapped[str | None] = mapped_column(String(100), nullable=True)
    commodity_type: Mapped[str | None] = mapped_column(String(150), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )

    last_contacted_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_follow_up_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lead_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100
    lead_temperature: Mapped[str | None] = mapped_column(String(10), nullable=True)  # Hot/Warm/Cold

    referral_source_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    do_not_contact: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Conversion tracking - set once a lead is converted (logic comes later,
    # these columns just hold the resulting linked records)
    converted_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    converted_to_opportunity: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)