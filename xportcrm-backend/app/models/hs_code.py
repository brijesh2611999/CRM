from sqlalchemy import String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class HSCode(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """HS Code Master (XPO-54 #8). 'code'=HS Code, 'name' holds
    the Description (consistent with how we handled Incoterms)."""

    __tablename__ = "hs_codes"

    duty_rate_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    gst_rate_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)