from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists,
    it returns None.
    
    :param email: str: Get the email address of the user
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
    
    :param body: UserModel: Validate the request body
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    new_user = User(**body.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.
    
    :param user: User: Pass the user object to the function
    :param token: str | None: Set the refresh token for a user
    :param db: Session: Write the updated token to the database
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.
    
    :param email: str: Get the email address of the user who is trying to confirm their account
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def new_password(user: User, password: str, db: Session) -> None:
    """
    The new_password function takes a user object, a password string, and a database session.
    It sets the user's password to the given password and commits it to the database.
    
    :param user: User: Pass in the user object
    :param password: str: Pass the new password to the function
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user.password = password
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function takes in an email and a url,
    and updates the avatar of the user with that email to be the given url.
    It returns a User object.
    
    :param email: Get the user from the database
    :param url: str: Specify the type of the url parameter
    :param db: Session: Pass the database session to the function
    :return: The user that was updated
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
