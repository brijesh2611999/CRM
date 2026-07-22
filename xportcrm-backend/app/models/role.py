import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Role(Base):
    """Minimal role definition for now (XPO-41 Role Management).
    Full permission matrix (module-level CRUDAE flags, field-level
    security, approval rights) will be added as separate tables later -
    this just gives Users something to reference so we can start
    building CRM tables that need created_by/assigned_to.

    Roles are tenant-scoped: each tenant can define/customize their
    own roles (XPO-41: 'Tenant Admin can create unlimited custom roles')."""

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    data_scope: Mapped[str] = mapped_column(String(20), nullable=False, default="Own")
    # Own / Team / Branch / All - XPO-41 Data Access Security
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )