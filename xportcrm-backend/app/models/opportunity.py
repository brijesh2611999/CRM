from datetime import datetime, date
import uuid

from sqlalchemy import String, Text, Numeric, Integer, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, AuditMixin, SoftDeleteMixin


class Opportunity(Base, UUIDPKMixin, TenantMixin, AuditMixin, SoftDeleteMixin):
    """Opportunity Module (XPO-47). Qualified sales opportunities
    tracked from Discovery through Closed Won/Lost."""

    __tablename__ = "opportunities"

    opportunity_name: Mapped[str] = mapped_column(String(200), nullable=False)

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True
    )
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True
    )

    opportunity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Air / Ocean FCL / Ocean LCL / Transport / Customs / Integrated

    stage: Mapped[str] = mapped_column(String(20), nullable=False, default="Discovery")
    # Discovery / Quote Sent / Proposal / Negotiation / Closed Won / Closed Lost

    estimated_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    expected_close_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    probability_pct: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100

    origin: Mapped[str | None] = mapped_column(String(150), nullable=True)
    destination: Mapped[str | None] = mapped_column(String(150), nullable=True)
    commodity: Mapped[str | None] = mapped_column(String(200), nullable=True)
    hs_code: Mapped[str | None] = mapped_column(String(15), nullable=True)
    estimated_volume: Mapped[str | None] = mapped_column(String(100), nullable=True)
    competitors: Mapped[str | None] = mapped_column(Text, nullable=True)

    win_loss_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    loss_reason_category: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # Price / Capacity / Service / Relationship / Other

    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_action_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    assigned_to_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    last_activity_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    quote_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)