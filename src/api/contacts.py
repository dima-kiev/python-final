from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.database.db import get_db
from src.services.auth import get_current_user
from src.database.models import Contact
from src.schemas import ContactModel, ContactUpdate, ContactResponse, UserResponse
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
) -> List[Contact]:
    """
    Get a list of the current User's Contacts with pagination. Accepts optional parameters: first_name, last_name, email.

    Args:
        skip (int): The number of Contacts to skip.
        limit (int): The maximum number of Contacts to return.
        first_name (Optional[str]): Filter by the first name (optional).
        last_name (Optional[str]): Filter by the last name (optional).
        email (Optional[str]): Filter by the email address (optional).

    Returns:
        List[Contact]: A list of Contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(
        skip, limit, user, first_name, last_name, email
    )
    return contacts


@router.get("/birthdays", response_model=List[ContactResponse])
async def read_contacts_with_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
) -> List[Contact]:
    """
    Retrieve a list of current User's Contacts who have birthdays in the next 7 days.

    Returns:
        List[Contact]: A list of Contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts_with_upcoming_birthdays(user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
) -> Contact:
    """
    Get a current User's Contact by its id.

    Args:
        contact_id (int): The id of the Contact to retrieve.

    Returns:
        Contact: The Contact with the specified id.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
) -> Contact:
    """
    Create a new current User's Contact with the given attributes.

    Args:
        body (ContactModel): A ContactModel with the attributes to assign to the Contact.

    Returns:
        Contact: A Contact with the assigned attributes.
    """
    contact_service = ContactService(db)
    try:
        return await contact_service.create_contact(body, user)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=e.errors()
        )


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
) -> Contact:
    """
    Update a current User's Contact by its id with the given attributes.

    Args:
        contact_id (int): The id of the Contact to update.
        body (ContactUpdate): A ContactUpdate with the attributes to assign to the Contact.

    Returns:
        Contact: The updated Contact with the specified id.
    """
    contact_service = ContactService(db)
    try:
        contact = await contact_service.update_contact(contact_id, body, user)
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
            )
        return contact
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=e.errors()
        )


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
) -> Contact:
    """
    Delete a current User's Contact by its id.

    Args:
        contact_id (int): The id of the Contact to delete.

    Returns:
        Contact: The deleted Contact with the specified id.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
