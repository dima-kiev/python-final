from datetime import datetime


def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json={
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "test@gmail.com",
            "phone": "0630000000",
            "birthday": datetime.now().date().strftime("%Y-%m-%d"),
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["last_name"] == "last_name"
    assert "id" in data


def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["last_name"] == "last_name"
    assert "id" in data


def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["last_name"] == "last_name"
    assert "id" in data[0]


def test_get_contacts_with_upcoming_birthdays(client, get_token):
    response = client.get(
        "/api/contacts/birthdays", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["last_name"] == "last_name"
    assert "id" in data[0]


def test_update_contact(client, get_token):
    response = client.put(
        "/api/contacts/1",
        json={"last_name": "new"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["last_name"] == "new"
    assert "id" in data


def test_update_contact_not_found(client, get_token):
    response = client.put(
        "/api/contacts/2",
        json={"last_name": "new"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["last_name"] == "new"
    assert "id" in data


def test_repeat_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"
