from unittest.mock import patch

from conftest import test_user


def test_get_me(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/users/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "avatar" in data


@patch("src.services.upload_file.UploadFileService.upload_file")
def test_update_avatar_user(mock_upload_file, client, get_token):
    fake_url = "<http://example.com/avatar.jpg>"
    mock_upload_file.return_value = fake_url

    headers = {"Authorization": f"Bearer {get_token}"}

    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

    response = client.patch("/api/users/avatar", headers=headers, files=file_data)

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert data["avatar"] == fake_url

    mock_upload_file.assert_called_once()


def test_update_user_password_failed_validation(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}

    json_data = {"old_password": "Testtest1!", "new_password": "123"}

    response = client.patch("/api/users/password", headers=headers, json=json_data)

    assert response.status_code == 422, response.text


def test_update_user_password(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}

    json_data = {"old_password": "Testtest1!", "new_password": "SomeNewPass1!"}

    response = client.patch("/api/users/password", headers=headers, json=json_data)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
