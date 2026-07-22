import uuid
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin


class Permission(Base, UUIDPKMixin, TenantMixin):
    """XPO-41 Permission Matrix: one row per (Role, Module, Action).
    Example: role_id=<Sales Exec>, module='Leads', action='create',
    allowed=True."""

    __tablename__ = "permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False, index=True
    )
    module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # e.g. 'leads', 'contacts', 'accounts', 'opportunities', 'quotations',
    # 'activities', 'masters', 'reports', 'settings', 'dashboards'

    action: Mapped[str] = mapped_column(String(20), nullable=False)
    # e.g. 'create', 'read', 'update', 'delete', 'approve', 'export', 'print', 'share'

    allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)