from datetime import date, datetime
import uuid

from sqlalchemy import String, Text, Numeric, Integer, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, AuditMixin, SoftDeleteMixin


class Quotation(Base, UUIDPKMixin, TenantMixin, AuditMixin, SoftDeleteMixin):
    """Quotation Module (XPO-49) - header record.
    'quote_number' is auto-generated per Numbering Configuration
    (numbering setup itself is a Settings-module concern, built later)."""

    __tablename__ = "quotations"

    quote_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    previous_quote_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quotations.id"), nullable=True
    )

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True
    )

    service_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Air / Ocean FCL / Ocean LCL / Transport / Customs / Integrated

    origin: Mapped[str | None] = mapped_column(String(150), nullable=True)
    destination: Mapped[str | None] = mapped_column(String(150), nullable=True)
    commodity: Mapped[str | None] = mapped_column(String(250), nullable=True)
    hs_code: Mapped[str | None] = mapped_column(String(15), nullable=True)
    weight: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    volume: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)

    container_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("container_types.id"), nullable=True
    )
    incoterm_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incoterms.id"), nullable=True
    )
    currency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False
    )

    valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Draft")
    # Draft / Sent / Accepted / Rejected / Expired

    payment_terms: Mapped[str | None] = mapped_column(String(30), nullable=True)
    terms_and_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Quote Summary (calculated fields - populated by service layer from charge lines)
    total_buy_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_sell_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    margin_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    margin_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    taxes: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    grand_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)

    # Approval Information
    approval_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approval_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_remarks: Mapped[str | None] = mapped_column(Text, nullable=True)