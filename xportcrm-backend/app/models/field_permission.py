import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin


class FieldPermission(Base, UUIDPKMixin):
    """XPO-41 Field-Level Security: per-role visibility for sensitive
    fields (Discount %, Margin %, Revenue, Cost, Credit Limit, Tax
    Details, etc.) on a given module."""

    __tablename__ = "field_permissions"

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False, index=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. 'accounts', 'quotations'
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. 'credit_limit', 'margin_pct'
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="Editable")
    # Hidden / ReadOnly / Editable