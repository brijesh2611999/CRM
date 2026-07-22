import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date, datetime

class LeadBase(BaseModel):
    company_name: str
    contact_person: str
    email: EmailStr | None = None
    phone: str | None = None
    mobile: str | None = None
    lead_source: str | None = None
    lead_status: str = "New"
    industry: str | None = None
    service_interest: str | None = None
    origin_region: str | None = None
    destination_region: str | None = None
    estimated_monthly_volume: str | None = None
    commodity_type: str | None = None
    notes: str | None = None
    assigned_to_id: uuid.UUID | None = None
    last_contacted_date: datetime | None = None
    next_follow_up_date: datetime | None = None
    lead_score: int | None = None
    lead_temperature: str | None = None
    referral_source_name: str | None = None
    do_not_contact: bool = False


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    company_name: str | None = None
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    mobile: str | None = None
    lead_source: str | None = None
    lead_status: str | None = None
    industry: str | None = None
    service_interest: str | None = None
    origin_region: str | None = None
    destination_region: str | None = None
    estimated_monthly_volume: str | None = None
    commodity_type: str | None = None
    notes: str | None = None
    assigned_to_id: uuid.UUID | None = None
    last_contacted_date: datetime | None = None
    next_follow_up_date: datetime | None = None
    lead_score: int | None = None
    lead_temperature: str | None = None
    referral_source_name: str | None = None
    do_not_contact: bool | None = None


class LeadRead(LeadBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    converted_account_id: uuid.UUID | None = None
    converted_to_opportunity: bool
    created_at: datetime
    modified_at: datetime | None = None


class LeadConvertResponse(BaseModel):
    lead_id: uuid.UUID
    account_id: uuid.UUID
    message: str = "Lead converted to Account successfully"

class ConvertToOpportunityRequest(BaseModel):
    opportunity_name: str
    opportunity_type: str
    estimated_amount: float | None = None
    expected_close_date: date | None = None