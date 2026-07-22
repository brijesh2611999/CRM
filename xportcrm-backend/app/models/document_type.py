from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class DocumentType(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Document Type Master (XPO-54 #15). 'code'=Document Code, 'name'=Document Name."""

    __tablename__ = "document_types"

    module: Mapped[str] = mapped_column(String(100), nullable=False)
    # CRM/Ops/Finance - stored comma-separated for multi-select (Option A pattern)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)