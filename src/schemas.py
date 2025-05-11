from datetime import date, datetime
from typing import List, Optional
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    validator,
    root_validator,
    constr,
    field_validator,
    EmailStr,
)
from src.database.models import UserRole
import re


class RequestEmail(BaseModel):
    email: EmailStr


class RequestPassword(BaseModel):
    old_password: str
    new_password: str = Field(
        min_length=8,
        max_length=24,
        description="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character.",
    )

    @field_validator("new_password")
    def password_complexity(cls, value):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"
        if not re.match(pattern, value):
            raise ValueError(
                "Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
            )
        return value


class UserModel(BaseModel):
    email: EmailStr = Field(max_length=50)
    username: str = Field(max_length=50)
    role: Optional[UserRole]


class UserResponse(UserModel):
    id: int
    created_at: datetime | None
    confirmed: bool
    avatar: Optional[str] = Field(None, max_length=255)
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserModel):
    password: str = Field(
        min_length=8,
        max_length=24,
        description="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character.",
    )

    @field_validator("password")
    def password_complexity(cls, value):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"
        if not re.match(pattern, value):
            raise ValueError(
                "Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
            )
        return value


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class ContactModel(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr = Field(max_length=50)
    phone: str = Field(max_length=50)
    birthday: date | None
    description: Optional[str] = Field(None, max_length=150)


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=50)
    birthday: Optional[date] = None
    description: Optional[str] = Field(None, max_length=150)

    @root_validator(pre=True)
    def check_at_least_one_field(cls, values):
        if all(value is None for value in values.values()):
            raise ValueError("At least one field must be provided")
        return values


class ContactResponse(ContactModel):
    id: int
    model_config = ConfigDict(from_attributes=True)
