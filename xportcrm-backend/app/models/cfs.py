import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class CFS(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """CFS Master (XPO-54 #3) - Container Freight Station.
    'code'=CFS Code, 'name'=CFS Name."""

    __tablename__ = "cfs"

    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ports.id"), nullable=False, index=True
    )
    contact_person: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mobile_no: Mapped[str | None] = mapped_column(String(15), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)