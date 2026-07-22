import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class QuotationBase(BaseModel):
    opportunity_id: uuid.UUID
    account_id: uuid.UUID
    service_type: str
    origin: str | None = None
    destination: str | None = None
    commodity: str | None = None
    hs_code: str | None = None
    weight: float | None = None
    volume: float | None = None
    container_type_id: uuid.UUID | None = None
    incoterm_id: uuid.UUID | None = None
    currency_id: uuid.UUID
    valid_until: date
    payment_terms: str | None = None
    terms_and_conditions: str | None = None
    notes: str | None = None


class QuotationCreate(QuotationBase):
    pass


class QuotationUpdate(BaseModel):
    service_type: str | None = None
    origin: str | None = None
    destination: str | None = None
    commodity: str | None = None
    hs_code: str | None = None
    weight: float | None = None
    volume: float | None = None
    container_type_id: uuid.UUID | None = None
    incoterm_id: uuid.UUID | None = None
    currency_id: uuid.UUID | None = None
    valid_until: date | None = None
    status: str | None = None
    payment_terms: str | None = None
    terms_and_conditions: str | None = None
    notes: str | None = None


class QuotationRead(QuotationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    quote_number: str
    revision_number: int
    previous_quote_id: uuid.UUID | None = None
    status: str
    total_buy_amount: float
    total_sell_amount: float
    margin_amount: float
    margin_pct: float
    taxes: float
    grand_total: float
    approval_status: str | None = None
    approved_by_id: uuid.UUID | None = None
    approval_date: datetime | None = None
    approval_remarks: str | None = None
    created_at: datetime
    modified_at: datetime | None = None


# --- Charge Line schemas ---

class ChargeLineBase(BaseModel):
    charge_head_id: uuid.UUID | None = None
    description: str | None = None
    quantity: float = 1
    buy_rate: float = 0
    sell_rate: float = 0
    is_taxable: bool = False
    sort_order: int = 0


class ChargeLineCreate(ChargeLineBase):
    pass


class ChargeLineUpdate(BaseModel):
    charge_head_id: uuid.UUID | None = None
    description: str | None = None
    quantity: float | None = None
    buy_rate: float | None = None
    sell_rate: float | None = None
    is_taxable: bool | None = None
    sort_order: int | None = None


class ChargeLineRead(ChargeLineBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    quotation_id: uuid.UUID
    buy_amount: float
    sell_amount: float