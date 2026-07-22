import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class AccountBase(BaseModel):
    code: str
    name: str
    account_type: str
    gstin: str | None = None
    pan: str | None = None
    iec_code: str | None = None
    billing_address: str | None = None
    shipping_address: str | None = None
    country: str
    primary_contact_name: str
    primary_contact_email: EmailStr
    primary_contact_phone: str | None = None
    secondary_contact_name: str | None = None
    secondary_contact_email: EmailStr | None = None
    credit_limit: float | None = None
    credit_days: int | None = None
    payment_terms: str | None = None
    parent_account_id: uuid.UUID | None = None
    tags: str | None = None
    account_rating: str | None = None
    preferred_currency_id: uuid.UUID | None = None
    preferred_lanes: str | None = None
    key_commodities: str | None = None
    annual_revenue_potential: float | None = None
    kyc_status: str | None = None
    blacklist_reason: str | None = None
    assigned_account_manager_id: uuid.UUID | None = None
    status: str = "Active"


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    # all fields optional for partial update
    code: str | None = None
    name: str | None = None
    account_type: str | None = None
    gstin: str | None = None
    pan: str | None = None
    iec_code: str | None = None
    billing_address: str | None = None
    shipping_address: str | None = None
    country: str | None = None
    primary_contact_name: str | None = None
    primary_contact_email: EmailStr | None = None
    primary_contact_phone: str | None = None
    secondary_contact_name: str | None = None
    secondary_contact_email: EmailStr | None = None
    credit_limit: float | None = None
    credit_days: int | None = None
    payment_terms: str | None = None
    parent_account_id: uuid.UUID | None = None
    tags: str | None = None
    account_rating: str | None = None
    preferred_currency_id: uuid.UUID | None = None
    preferred_lanes: str | None = None
    key_commodities: str | None = None
    annual_revenue_potential: float | None = None
    kyc_status: str | None = None
    blacklist_reason: str | None = None
    assigned_account_manager_id: uuid.UUID | None = None
    status: str | None = None


class AccountRead(AccountBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None