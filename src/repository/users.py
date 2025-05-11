from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize a UserRepository.

        Args:
            session (AsyncSession): An AsyncSession object connected to the database.
        """
        self.db = session

    async def confirm_email(self, email: EmailStr) -> None:
        """
        Confirm email address.

        Args:
            email (EmailStr): Email address to confirm.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a User by its id.

        Args:
            user_id (int): The id of the User to retrieve.

        Returns:
            User | None: The User with the specified id, or None if no such User exists.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        """
        Get a User by its email address.

        Args:
            email (EmailStr): The email address of the User to retrieve.

        Returns:
            User | None: The User with the specified email address, or None if no such User exists.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a User by its username.

        Args:
            username (str): The username of the User to retrieve.

        Returns:
            User | None: The User with the specified username, or None if no such User exists.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: Optional[str] = None) -> User:
        """
        Create a User with the given attributes.

        Args:
            body (UserCreate): A UserCreate with the attributes to assign to the User.
            avatar (Optional[str]): Avatar URL.

        Returns:
            User: A User with the assigned attributes.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar_url(self, email: EmailStr, url: str) -> User | None:
        """
        Update a User's avatar URL by its email address.

        Args:
            email (EmailStr): The email address of the User which avatar URL should be updated.
            url (str): Avatar URL.

        Returns:
            User | None: The User with the specified email address with updated avatar, or None if no such User exists.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.avatar = url
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def update_hashed_password(
        self, email: EmailStr, hashed_password: str
    ) -> None:
        """
        Update a User's hashed password by its email address.

        Args:
            email (EmailStr): The email address of the User which hashed password should be updated.
            hashed_password (str): Hashed password.
        """
        user = await self.get_user_by_email(email)
        user.hashed_password = hashed_password
        await self.db.commit()

    async def update_refresh_token(self, email: EmailStr, refresh_token: str) -> User:
        """
        Update a User's refresh token by its email address.

        Args:
            email (EmailStr): The email address of the User which refresh token should be updated.
            refresh_token (str): Refresh token.

        Returns:
            User: The User with the specified email address with updated refresh token.
        """
        user = await self.get_user_by_email(email)
        user.refresh_token = refresh_token
        await self.db.commit()
        await self.db.refresh(user)
        return user
