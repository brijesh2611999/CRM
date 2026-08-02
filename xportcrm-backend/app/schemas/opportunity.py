import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


# Stage -> Probability auto-suggestion map, per XPO-47 spec table
STAGE_PROBABILITY_MAP = {
    "Discovery": 10,
    "Quote": 30,
    "Proposal": 50,
    "Negotiation": 70,
    "Closed Won": 100,
    "Closed Lost": 0,
}


class OpportunityBase(BaseModel):
    opportunity_name: str
    account_id: uuid.UUID
    contact_id: uuid.UUID | None = None
    opportunity_type: str
    stage: str = "Discovery"
    estimated_amount: float | None = None
    expected_close_date: date | None = None
    probability_pct: int | None = None
    origin: str | None = None
    destination: str | None = None
    commodity: str | None = None
    hs_code: str | None = None
    estimated_volume: str | None = None
    competitors: str | None = None
    win_loss_reason: str | None = None
    loss_reason_category: str | None = None
    next_action: str | None = None
    next_action_date: datetime | None = None
    assigned_to_id: uuid.UUID


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    opportunity_name: str | None = None
    contact_id: uuid.UUID | None = None
    opportunity_type: str | None = None
    stage: str | None = None
    estimated_amount: float | None = None
    expected_close_date: date | None = None
    probability_pct: int | None = None
    origin: str | None = None
    destination: str | None = None
    commodity: str | None = None
    hs_code: str | None = None
    estimated_volume: str | None = None
    competitors: str | None = None
    win_loss_reason: str | None = None
    loss_reason_category: str | None = None
    next_action: str | None = None
    next_action_date: datetime | None = None
    assigned_to_id: uuid.UUID | None = None


class OpportunityRead(OpportunityBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    account_name: str | None = None
    contact_name: str | None = None
    last_activity_date: datetime | None = None
    quote_count: int
    created_at: datetime
    modified_at: datetime | None = None