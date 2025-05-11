import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, UserRole
from src.repository.users import UserRepository
from src.schemas import UserModel, UserCreate, UserResponse


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.mark.asyncio
async def test_confirm_email(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        email="test@gmail.com",
        username="test",
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    await user_repository.confirm_email(email="test@gmail.com")

    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        email="test@gmail.com",
        username="test",
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_id(user_id=1)

    assert result is not None
    assert isinstance(result, User)
    assert result.id == 1
    assert result.username == "test"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        email="test@gmail.com",
        username="test",
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_email(email="test@gmail.com")

    assert result is not None
    assert isinstance(result, User)
    assert result.id == 1
    assert result.username == "test"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        email="test@gmail.com",
        username="test",
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_username(username="test")

    assert result is not None
    assert isinstance(result, User)
    assert result.id == 1
    assert result.username == "test"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    user_data = UserCreate(
        email="test@gmail.com",
        username="test",
        password="Testtest1!",
        role=UserRole.ADMIN,
    )

    result = await user_repository.create_user(body=user_data)

    assert result is not None
    assert isinstance(result, User)
    assert result.username == "test"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session):
    existing_user = User(
        id=1,
        email="test@gmail.com",
        username="test",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.update_avatar_url(email="test@gmail.com", url="url")

    assert result is not None
    assert isinstance(result, User)
    assert result.username == "test"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_user)


@pytest.mark.asyncio
async def test_update_hashed_password(user_repository, mock_session):
    existing_user = User(
        id=1,
        email="test@gmail.com",
        username="test",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    await user_repository.update_hashed_password(
        email="test@gmail.com", hashed_password="tmp"
    )

    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_refresh_token(user_repository, mock_session):
    existing_user = User(
        id=1,
        email="test@gmail.com",
        username="test",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.update_refresh_token(
        email="test@gmail.com", refresh_token="tmp"
    )

    assert result is not None
    assert isinstance(result, User)
    assert result.username == "test"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_user)
