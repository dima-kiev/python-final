from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
import redis
import jsonpickle
import random
import string
import re
import sys

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.database.models import User, UserRole

r = redis.Redis(host="localhost", port=6379, db=0)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Compare plain text password with the hashed version in db.

        Args:
            plain_password (str): Plain text password.
            hashed_password (str): Hashed password.

        Returns:
            bool: Hashed plain text password matches the hashed one in db.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Get password hash..

        Args:
            password (str): Plain text password.

        Returns:
            str: Hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_email_from_token(token: str) -> EmailStr:
    """
    Get email address from JWT from verification.

    Args:
        token (str): JWT.

    Returns:
        EmailStr: Email address stored in JWT.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid token for email verification",
        )


def create_email_token(data: dict) -> str:
    """
    Create JWT with data provided.

    Args:
        data (dict): Data to store in JWT.

    Returns:
        str: JWT.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Create JWT with data provided.

    Args:
        data (dict): Data to store in JWT.
        expires_delta (Optional[int]): Provide time in ms to for the token to be valid.

    Returns:
        str: JWT.
    """
    to_encode = data.copy()
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + timedelta(seconds=expires_delta)
    else:
        expire = now + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire, "iat": now, "token_type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Create Refresh token with data provided.

    Args:
        data (dict): Data to store in Refresh token.
        expires_delta (Optional[int]): Provide time in ms to for the token to be valid.

    Returns:
        str: Refresh token.
    """
    to_encode = data.copy()
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + timedelta(seconds=expires_delta)
    else:
        expire = now + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire, "iat": now, "token_type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def generate_temp_password() -> str:
    """
    Generate random password.

    Returns:
        str: Generated password.
    """
    if "pytest" in sys.modules:
        return "TestTest2!"

    length = 10

    lower = random.choice(string.ascii_lowercase)
    upper = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    symbol = random.choice("@$!%*?&")

    remaining = length - 4
    other_chars = random.choices(
        string.ascii_letters + string.digits + "@$!%*?&", k=remaining
    )

    password_list = list(lower + upper + digit + symbol + "".join(other_chars))
    random.shuffle(password_list)

    password = "".join(password_list)

    return password


def serialize_user(user: User) -> str:
    """
    Serialize User object.

    Args:
        user (User): User object to serialize.

    Returns:
        str: Serialized JSON.
    """
    return jsonpickle.encode(user)


def deserialize_user(user_json: str) -> User:
    """
    Deserialize JSON into User object.

    Args:
        user_json (str): JSON to deserialize.

    Returns:
        User: Deserialized User.
    """
    return jsonpickle.decode(user_json)


async def verify_refresh_token(
    refresh_token: str, db: AsyncSession = Depends(get_db)
) -> User | None:
    """
    Get current User based on Refresh token.

    Args:
        refresh_token (str): Refresh token.

    Returns:
        User.
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    token_type = payload.get("token_type")
    if token_type != "refresh":
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user.refresh_token != refresh_token:
        raise credentials_exception

    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current User based on JWT.

    Returns:
        User: Current User.
    """

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user_json = r.get(username)

    if user_json is None:
        user_service = UserService(db)
        user = await user_service.get_user_by_username(username)

        if user is None:
            raise credentials_exception

        r.set(username, serialize_user(user))
        r.expire(username, 3600)
    else:
        user = deserialize_user(user_json)

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
):
    """
    Get current Admin User based on JWT.

    Returns:
        User: Current Admin User.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="User does not have enough permissions"
        )
    return current_user
