from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "Testtest1!",
    "role": "admin",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "User with this email already exists"


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email is not confirmed"


def test_not_confirmed_reset_password(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_reset_password_email", mock_send_email)
    response = client.post(
        "api/auth/forget_password", json={"email": user_data.get("email")}
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email is not confirmed"


def test_request_email(client):
    response = client.post(
        "api/auth/request_email", json={"email": user_data.get("email")}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert (
        data["message"]
        == "If this user exists in our database, we have sent them a confirmation email"
    )


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_repeat_request_email(client):
    response = client.post(
        "api/auth/request_email", json={"email": user_data.get("email")}
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Email is already confirmed"


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid username or password"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid username or password"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_reset_password(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_reset_password_email", mock_send_email)
    response = client.post(
        "api/auth/forget_password", json={"email": user_data.get("email")}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert (
        data["message"]
        == "If this user exists in our database, we have sent them an email with temporary password"
    )


@pytest.mark.asyncio
async def test_login_with_chaged_password(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": "TestTest2!",
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


@pytest.mark.asyncio
async def test_login_with_refresh_token(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": "TestTest2!",
        },
    )

    data = response.json()
    refresh_token = data.get("refresh_token")

    response = client.post(
        "api/auth/refresh-token", json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


@pytest.mark.asyncio
async def test_login_with_invalid_refresh_token(client):
    response = client.post(
        "api/auth/refresh-token", json={"refresh_token": "refresh_token"}
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Could not validate credentials"
