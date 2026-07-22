from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class ServiceType(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Service Type Master (XPO-54 #9). 'code'=Service Code, 'name'=Service Name."""

    __tablename__ = "service_types"

    category: Mapped[str] = mapped_column(String(20), nullable=False)
    # Air / Ocean / Transport / Customs
    description: Mapped[str | None] = mapped_column(Text, nullable=True)