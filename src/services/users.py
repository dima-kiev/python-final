from sqlalchemy.ext.asyncio import AsyncSession

from libgravatar import Gravatar
from pydantic import EmailStr

from src.repository.users import UserRepository
from src.database.models import User
from src.schemas import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        """
        Initialize a UserService.

        Args:
            db (AsyncSession): An AsyncSession object connected to the database.
        """
        self.repository = UserRepository(db)

    async def confirm_email(self, email: EmailStr) -> None:
        """
        Confirm email address.

        Args:
            email (EmailStr): Email address to confirm.
        """
        return await self.repository.confirm_email(email)

    async def create_user(self, body: UserCreate) -> User:
        """
        Create a User with the given attributes. Avatar will be retrieved from Gravatar automatically.

        Args:
            body (UserCreate): A UserCreate with the attributes to assign to the User.

        Returns:
            User: A User with the assigned attributes.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a User by its id.

        Args:
            user_id (int): The id of the User to retrieve.

        Returns:
            User | None: The User with the specified id, or None if no such User exists.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        """
        Get a User by its email address.

        Args:
            email (EmailStr): The email address of the User to retrieve.

        Returns:
            User | None: The User with the specified email address, or None if no such User exists.
        """
        return await self.repository.get_user_by_email(email)

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a User by its username.

        Args:
            username (str): The username of the User to retrieve.

        Returns:
            User | None: The User with the specified username, or None if no such User exists.
        """
        return await self.repository.get_user_by_username(username)

    async def update_avatar_url(self, email: EmailStr, url: str) -> User | None:
        """
        Update a User's avatar URL by its email address.

        Args:
            email (EmailStr): The email address of the User which avatar URL should be updated.
            url (str): Avatar URL.

        Returns:
            User | None: The User with the specified email address with updated avatar, or None if no such User exists.
        """
        return await self.repository.update_avatar_url(email, url)

    async def update_hashed_password(
        self, email: EmailStr, hashed_password: str
    ) -> None:
        """
        Update a User's hashed password by its email address.

        Args:
            email (EmailStr): The email address of the User which hashed password should be updated.
            hashed_password (str): Hashed password.
        """
        await self.repository.update_hashed_password(email, hashed_password)

    async def update_refresh_token(self, email: EmailStr, refresh_token: str) -> User:
        """
        Update a User's refresh token by its email address.

        Args:
            email (EmailStr): The email address of the User which refresh token should be updated.
            refresh_token (str): Refresh token.

        Returns:
            User: The User with the specified email address with updated refresh token.
        """
        await self.repository.update_refresh_token(email, refresh_token)
