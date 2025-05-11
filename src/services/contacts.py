from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.database.models import Contact
from src.schemas import ContactModel, ContactUpdate, UserResponse


class ContactService:
    def __init__(self, db: AsyncSession):
        """
        Initialize a ContactService.

        Args:
            db (AsyncSession): An AsyncSession object connected to the database.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: UserResponse) -> Contact:
        """
        Create a new Contact owned by `user` with the given attributes.

        Args:
            body (ContactModel): A ContactModel with the attributes to assign to the Contact.
            user (UserResponse): The owner of the Contact to create.

        Returns:
            Contact: A Contact with the assigned attributes.
        """
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        user: UserResponse,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> List[Contact]:
        """
        Get a list of Contacts owned by `user` with pagination. Accepts optional parameters: first_name, last_name, email.

        Args:
            skip (int): The number of Contacts to skip.
            limit (int): The maximum number of Contacts to return.
            user (UserResponse): The owner of the Contacts to retrieve.
            first_name (Optional[str]): Filter by the first name (optional).
            last_name (Optional[str]): Filter by the last name (optional).
            email (Optional[str]): Filter by the email address (optional).

        Returns:
            List[Contact]: A list of Contacts.
        """
        return await self.repository.get_contacts(
            skip, limit, user, first_name, last_name, email
        )

    async def get_contacts_with_upcoming_birthdays(
        self, user: UserResponse
    ) -> List[Contact]:
        """
        Retrieve a list of Contacts owned by `user` who have birthdays in the next 7 days.

        Args:
            user (UserResponse): The owner of the Contacts to retrieve.

        Returns:
            List[Contact]: A list of Contacts.
        """
        return await self.repository.get_contacts_with_upcoming_birthdays(user)

    async def get_contact(self, contact_id: int, user: UserResponse) -> Contact | None:
        """
        Get a Contact owned by `user` by its id.

        Args:
            contact_id (int): The id of the Contact to retrieve.
            user (UserResponse): The owner of the Contact to retrieve.

        Returns:
            Contact | None: The Contact with the specified id, or None if no such Contact exists.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: UserResponse
    ) -> Contact | None:
        """
        Update a Contact owned by `user` by its id with the given attributes.

        Args:
            contact_id (int): The id of the Contact to update.
            body (ContactUpdate): A ContactUpdate with the attributes to assign to the Contact.
            user (UserResponse): The owner of the Contact to update.

        Returns:
            Contact | None: The updated Contact with the specified id, or None if no such Contact exists.
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(
        self, contact_id: int, user: UserResponse
    ) -> Contact | None:
        """
        Delete a Contact owned by `user` by its id.

        Args:
            contact_id (int): The id of the Contact to delete.
            user (UserResponse): The owner of the Contact to delete.

        Returns:
            Contact | None: The deleted Contact with the specified id, or None if no such Contact exists.
        """
        return await self.repository.remove_contact(contact_id, user)
