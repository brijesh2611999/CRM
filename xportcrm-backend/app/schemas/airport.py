import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AirportBase(BaseModel):
    code: str
    name: str
    city: str
    country: str
    iata_code: str
    icao_code: str | None = None
    status: str = "Active"


class AirportCreate(AirportBase):
    pass


class AirportUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    city: str | None = None
    country: str | None = None
    iata_code: str | None = None
    icao_code: str | None = None
    status: str | None = None


class AirportRead(AirportBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None