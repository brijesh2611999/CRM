from datetime import date

from sqlalchemy import String, Text, Numeric, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin
import uuid


class Account(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Accounts - Customer/Vendor Master (XPO-45).
    'code' (from MasterFieldsMixin) used as an internal account code;
    'name' = Account Name. 'status' overloaded to also carry
    Active/Inactive/Blacklisted per spec (see account_type below)."""

    __tablename__ = "accounts"

    account_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Shipper / Consignee / CHA / Transporter / Freight Forwarder / Agent / Vendor

    gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    pan: Mapped[str | None] = mapped_column(String(10), nullable=True)
    iec_code: Mapped[str | None] = mapped_column(String(10), nullable=True)

    billing_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    shipping_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)

    primary_contact_name: Mapped[str] = mapped_column(String(150), nullable=False)
    primary_contact_email: Mapped[str] = mapped_column(String(150), nullable=False)
    primary_contact_phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    secondary_contact_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    secondary_contact_email: Mapped[str | None] = mapped_column(String(150), nullable=True)

    credit_limit: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    credit_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # Advance / 15 Days / 30 Days / 60 Days

    parent_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )

    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # comma-separated for now; see note below

    account_rating: Mapped[str | None] = mapped_column(String(5), nullable=True)  # A/B/C/D
    preferred_currency_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=True
    )
    preferred_lanes: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_commodities: Mapped[str | None] = mapped_column(Text, nullable=True)
    annual_revenue_potential: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    kyc_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Pending / Verified / Rejected

    blacklist_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    assigned_account_manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )