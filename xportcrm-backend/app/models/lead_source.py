from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, MasterFieldsMixin


class LeadSourceMaster(Base, UUIDPKMixin, TenantMixin, MasterFieldsMixin):
    """Lead Source Master (XPO-54 #13). 'code'=Source Code, 'name'=Source Name.
    No extra fields beyond the common master fields.

    Note: this is a separate, simple master table used for the Lead Source
    *dropdown options* that admins manage (Settings > Masters). It's
    different from the 'lead_source' text field already on the Lead
    table itself (which just stores the chosen value as free text for
    now, not a foreign key to this table) - we can wire that FK later
    once we build the Leads API and want strict validation against
    this master list."""

    __tablename__ = "lead_source_masters"