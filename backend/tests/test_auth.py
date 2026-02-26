"""
Test Suite - Authentication Tests
Run: pytest tests/test_auth.py -v
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_duplicate_email():
    """Test duplicate email registration fails"""
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "testpass123"
        }
    )

    # Duplicate registration
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 400


def test_login_success():
    """Test successful login"""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "testpass123"
        }
    )

    # Login
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "email": "login@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with wrong password fails"""
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "email": "login@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user info with token"""
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "current@example.com",
            "password": "testpass123"
        }
    )

    login_response = client.post(
        "/api/v1/auth/login/json",
        json={
            "email": "current@example.com",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"


def test_unauthorized_access():
    """Test accessing protected route without token fails"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
