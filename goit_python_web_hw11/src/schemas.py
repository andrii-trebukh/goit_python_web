import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ContactsBase(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone: str = Field(pattern=r"^\d{10}$")
    birthday: datetime.date
    miscellaneous: Optional[str] = None


class GetContactResponce(ContactsBase):
    id: int


class PostContactRequest(ContactsBase):
    pass


class PatchContactRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(pattern=r"^\d{10}$", default=None)
    birthday: Optional[datetime.date] = None
    miscellaneous: Optional[str] = None
