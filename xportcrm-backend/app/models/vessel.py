from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class Vessel(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Vessel Master (XPO-54 #4). 'name'=Vessel Name (from mixin).
    Note: spec has no separate 'Code' for Vessel - we still inherit
    'code' from MasterFieldsMixin for consistency across masters,
    but it can be left blank/auto if not meaningful for vessels."""

    __tablename__ = "vessels"

    imo_number: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    flag_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    operator: Mapped[str | None] = mapped_column(String(150), nullable=True)
    vessel_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Container / Bulk / Tanker