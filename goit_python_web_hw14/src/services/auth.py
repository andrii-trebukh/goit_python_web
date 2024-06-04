import pickle
import redis
import datetime
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository.users import get_user_by_email
from src.conf.config import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashes it
        using the same salt that was used to hash the stored password. If the two hashes match,
        then we know that the user has entered in their correct password.
        
        :param plain_password: Compare the password entered by the user with the hashed_password
        :param hashed_password: Compare the hashed password in the database with the plain_password parameter
        :return: A boolean value
        :doc-author: Trelent
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password and returns the hashed version of it.
        The hashing algorithm is defined in the settings file.
        
        :param password: str: Pass in the password that is being hashed
        :return: A hash of the password
        :doc-author: Trelent
        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None
    ):
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): A dictionary of key-value pairs to include in the JWT payload.
                expires_delta (Optional[float]): An optional timedelta for the expiration time of the token. Defaults to 15 minutes if not provided.
        
        :param data: dict: Pass the data that will be encoded in the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: An encoded access token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=expires_delta)
        else:
            expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
        to_encode.update(
            {
                "iat": datetime.datetime.now(datetime.UTC),
                "exp": expire,
                "scope": "access_token"
            }
        )
        encoded_access_token = jwt.encode(
            to_encode,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None
    ):
        """
        The create_refresh_token function creates a refresh token for the user.
        
        :param data: dict: Pass the user's id and username to the function
        :param expires_delta: Optional[float]: Set the expiration time for the refresh token
        :return: A refresh token that is encoded with the user's id, email, and username
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=expires_delta)
        else:
            expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
        to_encode.update(
            {
                "iat": datetime.datetime.now(datetime.UTC),
                "exp": expire,
                "scope": "refresh_token"
            }
        )
        encoded_refresh_token = jwt.encode(
            to_encode,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function decodes the refresh token and returns the email of the user.
        If it fails to decode, it raises an HTTPException with a 401 status code.
        
        :param refresh_token: str: Pass in the refresh token that we want to decode
        :return: The email of the user if the refresh token is valid
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(
                refresh_token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid scope for token'
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials'
            )

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ):
        """
        The get_current_user function is a dependency that can be used to get the current user.
        It will check if the token is valid and return an User object.
        If it's not valid, it will raise an HTTPException with status 401 (Unauthorized).
        
        :param token: str: Pass the token to the function
        :param db: Session: Pass the database session to the function
        :return: The current user, which is a user object
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = self.r.get(f"user:{email}")
        if user is None:
            user = await get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user
    
    def create_email_token(self, data: dict):
        """
        The create_email_token function creates a token that is used to verify the user's email address.
        The token is created using the JWT library and contains information about when it was issued, 
        when it expires, and what email address it belongs to. The function returns this token.
        
        :param data: dict: Pass the data that will be encoded into the token
        :return: A token that is used to verify the user's email address
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
        to_encode.update({"iat": datetime.datetime.now(datetime.UTC), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        The function first tries to decode the token using jwt.decode, which will raise a JWTError if it fails to decode the token.
        If decoding is successful, then we return the email address from within the payload of our decoded JWT.
        
        :param token: str: Pass in the token that was sent to the user's email address
        :return: The email address associated with the token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")
    
    async def create_password_reset_token(
        self,
        data: dict,
    ):
        """
        The create_password_reset_token function creates a password reset token.
        
        :param data: dict: Pass in the user's email address
        :return: A jwt token that has the following claims:
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
        to_encode.update(
            {
                "iat": datetime.datetime.now(datetime.UTC),
                "exp": expire,
                "scope": "password_reset_token"
            }
        )
        encoded_password_reset_token = jwt.encode(
            to_encode,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        return encoded_password_reset_token
    
    async def create_new_password_token(
        self,
        data: dict,
    ):
        """
        The create_new_password_token function creates a new password token for the user.
            The function takes in a dictionary of data, and returns an encoded password reset token.
        
        :param data: dict: Pass the user's email address to the function
        :return: An encoded password reset token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
        to_encode.update(
            {
                "iat": datetime.datetime.now(datetime.UTC),
                "exp": expire,
                "scope": "new_password_token"
            }
        )
        encoded_password_reset_token = jwt.encode(
            to_encode,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        return encoded_password_reset_token
    
    async def get_reset_password_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ):
        """
        The get_reset_password_user function is a helper function that takes in the token and database session as arguments.
        It then decodes the JWT, checks if it's a password reset token, and returns the user associated with that email address.
        
        :param token: str: Get the token from the authorization header
        :param db: Session: Get the database session
        :return: A user object
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            if payload['scope'] == 'password_reset_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user
    
    async def get_new_password_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ):
        """
        The get_new_password_user function is used to validate the JWT token that was sent in the email.
        It will return a user object if it is valid, otherwise it will raise an exception.
        
        :param token: str: Get the token from the request header
        :param db: Session: Pass the database session to the function
        :return: A user object
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            if payload['scope'] == 'new_password_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user



auth_service = Auth()
