from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class IndustryType(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Industry Type Master (XPO-54 #14). 'code'=Industry Code, 'name'=Industry Name.
    No extra fields."""

    __tablename__ = "industry_types"