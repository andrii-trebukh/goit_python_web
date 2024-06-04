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
    """
    The read_contacts function returns a list of contacts that match the search criteria.
    
    :param name_contains: Filter contacts by name
    :param surname_contains: Filter the contacts by surname
    :param email_contains: Filter the contacts by email
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(
        Contact.name.like(f"%{name_contains}%"),
        Contact.surname.like(f"%{surname_contains}%"),
        Contact.email.like(f"%{email_contains}%"),
        Contact.user_id == current_user.id
    ).all()
    return contacts


def birthdy_next_days(birthday: Mapped[datetime.date], days: int = 0):
    """
    The birthdy_next_days function returns True if the birthday is within
    the next `days` days, otherwise False.
    
    
    :param birthday: Mapped[datetime.date]: Map the birthday column to a datetime
    :param days: int: Specify the number of days to check for
    :return: A boolean value that indicates if the birthday is in the next days
    :doc-author: Trelent
    """
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
    """
    The get_birthdays function returns a list of contacts with birthdays in the next 7 days.
    
    :param next_days: int: Specify the number of days to look ahead for birthdays
    :param db: Session: Inject the database session
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
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
    """
    The read_contact function is used to retrieve a single contact from the database.
    It takes an integer as its first argument, which represents the ID of the contact
    to be retrieved. It also takes two optional arguments: db and current_user. The db 
    argument is used to pass in a database session object, while current_user is used 
    to pass in information about the user making this request.
    
    :param contact_id: int: Specify the id of the contact to be read
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
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
    """
    The create_contact function creates a new contact in the database.
    
    :param body: PostContactRequest: Validate the request body
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
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
    """
    The update_contact function updates a contact in the database.
    
    :param body: PostContactRequest: Validate the request body
    :param contact_id: int: Specify the contact we want to update
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
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
    """
    The patch_contact function patch a contact in the database.
    
    :param body: PostContactRequest: Validate the request body
    :param contact_id: int: Specify the contact we want to patch
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A contact object
    """
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
    """
    The remove_contact function removes a contact from the database.
    It takes in an integer, contact_id, and uses it to find the corresponding Contact object in the database.
    If no such Contact exists, then a 404 error is raised. Otherwise, that Contact is deleted from the database.
    
    :param contact_id: int: Identify the contact to delete
    :param db: Session: Get a database session
    :param current_user: User: Get the user that is currently logged in
    :return: The deleted contact
    :doc-author: Trelent
    """
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
