from datetime import date
import uuid

from sqlalchemy import String, Text, Boolean, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, AuditMixin, SoftDeleteMixin


class Contact(Base, UUIDPKMixin, TenantMixin, AuditMixin, SoftDeleteMixin):
    """Contacts Module (XPO-46). People associated with an Account.
    Note: unlike Port/Currency/etc., Contact doesn't use MasterFieldsMixin
    (no 'code' field in the spec) - it uses AuditMixin + SoftDeleteMixin
    directly instead, plus its own name/status fields below."""

    __tablename__ = "contacts"

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True
    )

    contact_name: Mapped[str] = mapped_column(String(100), nullable=False)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    email: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(15), nullable=True)
    whatsapp_number: Mapped[str | None] = mapped_column(String(15), nullable=True)
    linkedin_profile: Mapped[str | None] = mapped_column(String(255), nullable=True)

    role_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # Decision Maker / Influencer / End User / Finance / Operations

    is_primary_contact: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    do_not_contact: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)