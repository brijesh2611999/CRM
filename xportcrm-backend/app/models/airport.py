from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class Airport(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Airport Master (XPO-54 #2). 'code'=Airport Code, 'name'=Airport Name."""

    __tablename__ = "airports"

    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    iata_code: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    icao_code: Mapped[str | None] = mapped_column(String(4), nullable=True)