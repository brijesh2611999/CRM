import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AirlineBase(BaseModel):
    code: str
    name: str
    iata_code: str
    country: str
    status: str = "Active"


class AirlineCreate(AirlineBase):
    pass


class AirlineUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    iata_code: str | None = None
    country: str | None = None
    status: str | None = None


class AirlineRead(AirlineBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None