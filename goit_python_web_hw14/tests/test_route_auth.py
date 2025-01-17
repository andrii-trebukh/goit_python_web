from unittest.mock import MagicMock
import pytest

from src.database.models import User
from src.services.auth import auth_service


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_refresh_token(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    refresh_token = current_user.refresh_token
    response = client.get(
        "/api/auth/refresh_token",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_refresh_wrong_token(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    refresh_token = current_user.refresh_token
    current_user.refresh_token = None
    session.commit()
    response = client.get(
        "/api/auth/refresh_token",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid refresh token"


def test_already_confirmed_email(client, user):
    token = auth_service.create_email_token(
        {
            "sub": user.get("email")
        }
    )
    response = client.get(
        f"/api/auth/confirmed_email/{token}"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"


def test_confirmed_email(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()

    token = auth_service.create_email_token(
        {
            "sub": user.get("email")
        }
    )
    response = client.get(
        f"/api/auth/confirmed_email/{token}"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email confirmed"


def test_invalid_email(client):
    token = auth_service.create_email_token(
        {
            "sub": "invalid.email@example.com"
        }
    )
    response = client.get(
        f"/api/auth/confirmed_email/{token}"
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Verification error"


def test_already_confirmed_email_request(client, user):
    response = client.post(
        "/api/auth/request_email",
        json={"email": user.get('email')}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"


def test_email_request(client, user, monkeypatch, session):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()
    response = client.post(
        "/api/auth/request_email",
        json={"email": user.get('email')}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for confirmation."


def test_invalid_email_request(client):
    response = client.post(
        "/api/auth/request_email",
        json={"email": "invalid.email@example.com"}
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_forgot_password(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr(
        "src.routes.auth.send_reset_password_email",
        mock_send_email
    )
    response = client.post(
        "/api/auth/forgot_password",
        json={"email": user.get('email')}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for reset password."


def test_forgot_password_invalid_email(client):
    response = client.post(
        "/api/auth/forgot_password",
        json={"email": "invalid.email@example.com"}
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


@pytest.mark.asyncio
async def test_password_reset(client, user):
    token = await auth_service.create_password_reset_token(
        {
            "sub": user.get("email")
        }
    )
    response = client.get(
        f"/api/auth/password_reset/{token}"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_new_password(client, user):
    token = await auth_service.create_new_password_token(
        {
            "sub": user.get("email")
        }
    )
    response = client.patch(
        "/api/auth/new_password",
        json={"password": "987654321"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password has been changed."
