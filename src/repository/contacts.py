from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import extract, or_

from src.database.models import Contact
from src.schemas import ContactModel, ContactUpdate, UserResponse

from datetime import datetime, timedelta


class ContactRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize a ContactRepository.

        Args:
            session (AsyncSession): An AsyncSession object connected to the database.
        """
        self.db = session

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
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)

        if first_name:
            stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

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
        today = datetime.now().date()

        conditions = []
        for i in range(7):
            target_date = today + timedelta(days=i)
            condition = (extract("month", Contact.birthday) == target_date.month) & (
                extract("day", Contact.birthday) == target_date.day
            )
            conditions.append(condition)

        stmt = select(Contact).filter_by(user=user).where(or_(*conditions))

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(
        self, contact_id: int, user: UserResponse
    ) -> Contact | None:
        """
        Get a Contact owned by `user` by its id.

        Args:
            contact_id (int): The id of the Contact to retrieve.
            user (UserResponse): The owner of the Contact to retrieve.

        Returns:
            Contact | None: The Contact with the specified id, or None if no such Contact exists.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: UserResponse) -> Contact:
        """
        Create a new Contact owned by `user` with the given attributes.

        Args:
            body (ContactModel): A ContactModel with the attributes to assign to the Contact.
            user (UserResponse): The owner of the Contact to create.

        Returns:
            Contact: A Contact with the assigned attributes.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

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
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)
        return contact

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
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact
