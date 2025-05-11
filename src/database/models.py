from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    func,
    Table,
    Date,
    DateTime,
    Enum as SqlEnum,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.schema import ForeignKey


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(150), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="contacts")


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    avatar: Mapped[str] = mapped_column(String(255))
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="user")
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
