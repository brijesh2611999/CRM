import uuid

from sqlalchemy import String, Numeric, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, AuditMixin


class QuotationChargeLine(Base, UUIDPKMixin, TenantMixin, AuditMixin):
    """Multi-line charge items for a Quotation (XPO-49 section 3.3).
    Each line represents one charge (e.g. Ocean Freight, THC, Customs
    Clearance) with buy/sell amounts feeding into the Quote Summary."""

    __tablename__ = "quotation_charge_lines"

    quotation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quotations.id"), nullable=False, index=True
    )
    charge_head_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("charge_heads.id"), nullable=True
    )
    # Note: charge_heads table doesn't exist yet - we'll create it as
    # part of the remaining Masters (XPO-54 #12) right after this

    description: Mapped[str | None] = mapped_column(String(250), nullable=True)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1, nullable=False)
    buy_rate: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    buy_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    sell_rate: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    sell_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)