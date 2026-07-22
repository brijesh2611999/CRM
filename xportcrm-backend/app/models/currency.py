from sqlalchemy import String, Integer, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class Currency(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Currency Master (XPO-54 #6).
    'code' = Currency Code (ISO), 'name' = Currency Name."""

    __tablename__ = "currencies"

    symbol: Mapped[str] = mapped_column(String(5), nullable=False)
    decimal_places: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    is_base_currency: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)