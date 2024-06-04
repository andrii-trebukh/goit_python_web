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
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None
    ):
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
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
        to_encode.update({"iat": datetime.datetime.now(datetime.UTC), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    async def get_email_from_token(self, token: str):
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
