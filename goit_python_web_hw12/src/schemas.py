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


class UserModel(BaseModel):
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    email: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
