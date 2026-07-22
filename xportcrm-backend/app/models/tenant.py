import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Tenant(Base):
    """Represents one customer organization (SaaS tenant).
    Every business record (Lead, Account, Master row, etc.) belongs
    to exactly one Tenant via tenant_id - this is what keeps each
    customer's data isolated from every other customer (XPO-41).

    Tenant resolution approach: login-based. A user logs in at a
    single shared URL; their JWT/session carries their tenant_id
    (set at login, based on which org their user account belongs to).
    No subdomain/DNS routing involved."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )