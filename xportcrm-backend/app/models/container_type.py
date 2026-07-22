from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class ContainerType(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Container Type Master (XPO-54 #10).
    'code' = Container Type Code, 'name' = Container Type Name."""

    __tablename__ = "container_types"

    teu_factor: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    length_feet: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    max_weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)