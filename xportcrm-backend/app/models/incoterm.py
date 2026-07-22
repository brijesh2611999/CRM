from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class Incoterm(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Incoterms Master (XPO-54 #11).
    'code' = Incoterm Code (EXW, FOB, CIF...), 'name' = Description
    (per spec, both 'Code' and 'Description' are required text fields)."""

    __tablename__ = "incoterms"

    responsibility_summary: Mapped[str | None] = mapped_column(Text, nullable=True)