from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class Port(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Port Master (XPO-54 #1). Sea/Air ports used in shipment transactions.
    Inherited from MasterFieldsMixin: code, name, status, audit fields, soft delete.
    Here 'code' = Port Code, 'name' = Port Name."""

    __tablename__ = "ports"

    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    port_type: Mapped[str] = mapped_column(String(10), nullable=False)  # Sea / Air
    unlocode: Mapped[str | None] = mapped_column(String(15), nullable=True)