from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, \
    HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail, PaswordModel
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email, send_reset_password_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    The signup function creates a new user in the database.
    It takes a UserModel object as input, and returns a dictionary with the created user and an informative message.
    If there is already an account associated with that email address, it raises an HTTPException.
    
    :param body: UserModel: Get the user's email and password
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Get the database session
    :return: A dictionary with two keys: user and detail
    :doc-author: Trelent
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    The login function is used to authenticate a user.
    It takes the email and password from the request body,
    and returns an access token and refresh token if successful.
    
    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Get the database session
    :return: A jwt token
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(
        data={"sub": user.email}
    )
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": user.email}
    )
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """
    The refresh_token function is used to refresh the access token.
    It takes an HTTP Authorization header with a valid refresh token and returns a new access token.
    
    :param credentials: HTTPAuthorizationCredentials: Get the credentials from the request
    :param db: Session: Get the database session
    :return: A token object with the new access_token, refresh_token and token type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(
        data={"sub": email}
    )
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": email}
    )
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function takes a token and db as parameters.
    It then calls the get_email_from_token function from auth service, passing in the token parameter.
    The get email from token function returns an email address, which is assigned to the variable email.
    Next, we call repository users' get user by email function with our newly created variable and db as parameters. 
    This will return a user object or None if no such user exists in our database.
    
    :param token: str: Get the token from the url
    :param db: Session: Access the database
    :return: A message that the email is already confirmed or a message that the email is confirmed
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    The request_email function is used to request a confirmation email.
    It takes the user's email address as input and sends an email with a link that can be used to confirm the account.
    The function returns a message indicating whether or not the user has already confirmed their account.
    
    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Access the database
    :return: A message to the user
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.post('/forgot_password')
async def forgot_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    The forgot_password function is used to send an email to the user with a link
    to reset their password. The function takes in the user's email address and sends
    an email containing a link that will allow them to reset their password.
    
    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A message to the user
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email"
        )
    background_tasks.add_task(send_reset_password_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for reset password."}


@router.get('/password_reset/{token}')
async def password_reset(token: str, db: Session = Depends(get_db)):
    """
    The password_reset function is used to reset a user's password.
    It takes in the token that was sent to the user's email address and returns a new_password_token.
    The new_password_token can be used by the client application to update their password.
    
    :param token: str: Get the token from the request body
    :param db: Session: Access the database
    :return: A new token and token type
    :doc-author: Trelent
    """
    user = await auth_service.get_reset_password_user(token, db)
    # if user is None:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    new_password_token = await auth_service.create_new_password_token(
        data={"sub": user.email}
    )
    return {
        "new_password_token": new_password_token,
        "token_type": "bearer"
    }


@router.patch('/new_password')
async def new_password(
    body: PaswordModel,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """
    The new_password function is used to change a user's password.
        The function takes in the new password and then hashes it before storing it in the database.
        It also checks that the token provided by the user is valid.
    
    :param body: PaswordModel: Receive the new password from the user
    :param credentials: HTTPAuthorizationCredentials: Get the token from the header
    :param db: Session: Get a database session
    :return: A message that the password has been changed
    :doc-author: Trelent
    """
    token = credentials.credentials
    user = await auth_service.get_new_password_user(token, db)
    body.password = auth_service.get_password_hash(body.password)
    await repository_users.new_password(user, body.password, db)
    return {"message": "Password has been changed."}
