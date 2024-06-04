from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import func, extract, Interval
from sqlalchemy.orm import Session, Mapped
from fastapi_limiter.depends import RateLimiter
from src.database.db import get_db
from src.schemas import GetContactResponce, PostContactRequest, \
    PatchContactRequest
from src.database.models import Contact, User
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get(
    "/",
    response_model=List[GetContactResponce],
    description='No more than 10 requests per minute',
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def read_contacts(
    name_contains="",
    surname_contains="",
    email_contains="",
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contacts = db.query(Contact).filter(
        Contact.name.like(f"%{name_contains}%"),
        Contact.surname.like(f"%{surname_contains}%"),
        Contact.email.like(f"%{email_contains}%"),
        Contact.user_id == current_user.id
    ).all()
    return contacts


def birthdy_next_days(birthday: Mapped[datetime.date], days: int = 0):
    if days == 0:
        return False
    age = extract("year", func.age(birthday))
    birthday_days = birthday - func.cast(timedelta(days), Interval)
    age_days = extract("year", func.age(birthday_days))
    return age_days > age


@router.get("/birthdays", response_model=List[GetContactResponce])
async def get_birthdays(
    next_days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    return db.query(Contact).filter(
        birthdy_next_days(Contact.birthday, next_days),
        Contact.user_id == current_user.id
    )


@router.get("/{contact_id}", response_model=GetContactResponce)
async def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


@router.post(
    "/",
    response_model=GetContactResponce,
    status_code=status.HTTP_201_CREATED,
    description='No more than 10 requests per minute',
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def create_contact(
    body: PostContactRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contact = Contact(
        **body.model_dump(),
        user_id=current_user.id
    )
    db.add(contact)
    db.commit()
    return contact


@router.put("/{contact_id}", response_model=GetContactResponce)
async def update_contact(
    body: PostContactRequest,
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    for key, val in body.model_dump().items():
        setattr(contact, key, val)
    db.commit()
    return contact


@router.patch("/{contact_id}", response_model=GetContactResponce)
async def patch_contact(
    body: PatchContactRequest,
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    for key, val in body.model_dump().items():
        if val is None:
            continue
        setattr(contact, key, val)
    db.commit()
    return contact


@router.delete("/{contact_id}", response_model=GetContactResponce)
async def remove_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    db.delete(contact)
    db.commit()
    return contact
