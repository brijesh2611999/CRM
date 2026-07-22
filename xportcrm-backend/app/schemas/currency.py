import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CurrencyBase(BaseModel):
    code: str
    name: str
    symbol: str
    decimal_places: int = 2
    exchange_rate: float
    is_base_currency: bool = False
    status: str = "Active"


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    symbol: str | None = None
    decimal_places: int | None = None
    exchange_rate: float | None = None
    is_base_currency: bool | None = None
    status: str | None = None


class CurrencyRead(CurrencyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None