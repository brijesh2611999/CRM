from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class ChargeHead(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Charge Head Master (XPO-54 #12).
    'code' = Charge Code, 'name' = Charge Name.
    Used by Quotation Charge Line Items to categorize each charge
    (Ocean Freight, THC, Customs Clearance, etc.)."""

    __tablename__ = "charge_heads"

    category: Mapped[str] = mapped_column(String(20), nullable=False)
    # Freight / Origin / Destination / Other

    is_taxable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # tax_template lookup ("Tax Master") skipped for now - no Tax Master
    # exists yet in our build order; can be added as a nullable FK later
    # once a Tax Master table is built.