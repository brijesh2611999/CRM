from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class Airline(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Airline Master (XPO-54 #5). 'code'=Airline Code, 'name'=Airline Name."""

    __tablename__ = "airlines"

    iata_code: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)