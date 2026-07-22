from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class UnitOfMeasure(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Unit of Measure Master (XPO-54 #7). 'code'=UOM Code, 'name'=UOM Name."""

    __tablename__ = "units_of_measure"

    category: Mapped[str] = mapped_column(String(20), nullable=False)
    # Weight / Volume / Length / Count
    decimal_precision: Mapped[int | None] = mapped_column(Integer, nullable=True)