from sqlalchemy import Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class QuoteTncTemplate(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Quote T&C Template Master (XPO-54 #16). 'code'=Template Code,
    'name'=Template Name."""

    __tablename__ = "quote_tnc_templates"

    terms_and_conditions: Mapped[str] = mapped_column(Text, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)