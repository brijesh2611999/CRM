import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class ContactBase(BaseModel):
    account_id: uuid.UUID
    contact_name: str
    designation: str | None = None
    department: str | None = None
    email: EmailStr
    phone: str | None = None
    mobile: str | None = None
    whatsapp_number: str | None = None
    linkedin_profile: str | None = None
    role_type: str | None = None
    is_primary_contact: bool = False
    do_not_contact: bool = False
    birthday: date | None = None
    notes: str | None = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    contact_name: str | None = None
    designation: str | None = None
    department: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    mobile: str | None = None
    whatsapp_number: str | None = None
    linkedin_profile: str | None = None
    role_type: str | None = None
    is_primary_contact: bool | None = None
    do_not_contact: bool | None = None
    birthday: date | None = None
    notes: str | None = None


class ContactRead(ContactBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    modified_at: datetime | None = None