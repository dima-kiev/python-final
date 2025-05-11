import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate, ContactResponse
from src.services.auth import Hash

from datetime import datetime, timedelta


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1,
        username="testuser",
        email="test@gmail.com",
        confirmed=True,
        hashed_password=Hash().get_password_hash("Test1!"),
    )


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(
            id=1,
            first_name="first_name",
            last_name="last_name",
            email="test@gmail.com",
            phone="0630000000",
            birthday=datetime.now().date(),
            user=user,
        )
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    assert len(result) == 1
    assert result[0].last_name == "last_name"


@pytest.mark.asyncio
async def test_get_contacts_with_upcoming_birthdays(
    contact_repository, mock_session, user
):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(
            id=1,
            first_name="first_name",
            last_name="last_name",
            email="test@gmail.com",
            phone="0630000000",
            birthday=datetime.now().date(),
            user=user,
        ),
        Contact(
            id=2,
            first_name="first_name2",
            last_name="last_name2",
            email="test2@gmail.com",
            phone="0640000000",
            birthday=datetime.now().date() + timedelta(days=2),
            user=user,
        ),
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.get_contacts_with_upcoming_birthdays(user=user)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        first_name="first_name",
        last_name="last_name",
        email="test@gmail.com",
        phone="0630000000",
        birthday=datetime.now().date(),
        user=user,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    assert result is not None
    assert isinstance(result, Contact)
    assert result.id == 1
    assert result.last_name == "last_name"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    contact_data = ContactModel(
        first_name="first_name",
        last_name="last_name",
        email="test@gmail.com",
        phone="0630000000",
        birthday=datetime.now().date(),
        description="description",
    )

    result = await contact_repository.create_contact(body=contact_data, user=user)

    assert result is not None
    assert isinstance(result, Contact)
    assert result.last_name == "last_name"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    contact_data = ContactUpdate(last_name="new")
    existing_contact = Contact(
        id=1,
        first_name="first_name",
        last_name="last_name",
        email="test@gmail.com",
        phone="0630000000",
        birthday=datetime.now().date(),
        user=user,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    assert result is not None
    assert isinstance(result, Contact)
    assert result.last_name == "new"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    existing_contact = Contact(
        id=1,
        first_name="first_name",
        last_name="last_name",
        email="test@gmail.com",
        phone="0630000000",
        birthday=datetime.now().date(),
        user=user,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(contact_id=1, user=user)

    assert result is not None
    assert isinstance(result, Contact)
    assert result.last_name == "last_name"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
