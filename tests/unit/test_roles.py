import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock

from app.main import app
from app.models.user import User
from app.models.roles import UserRole, has_minimum_role
from app.auth.role_helpers import RoleChecker
from app.auth.dependencies import get_current_user


# ==============================================================================
# 1. Tests for Role Enum and Hierarchy
# ==============================================================================
def test_role_enum_values():
    assert UserRole.OWNER == "owner"
    assert UserRole.ADMIN == "admin"
    assert UserRole.MANAGER == "manager"
    assert UserRole.STAFF == "staff"
    assert UserRole.VIEWER == "viewer"


def test_has_minimum_role_checks():
    # OWNER checks (highest privilege)
    assert has_minimum_role(UserRole.OWNER, UserRole.OWNER) is True
    assert has_minimum_role(UserRole.OWNER, UserRole.ADMIN) is True
    assert has_minimum_role(UserRole.OWNER, UserRole.VIEWER) is True

    # ADMIN checks
    assert has_minimum_role(UserRole.ADMIN, UserRole.OWNER) is False
    assert has_minimum_role(UserRole.ADMIN, UserRole.ADMIN) is True
    assert has_minimum_role(UserRole.ADMIN, UserRole.MANAGER) is True
    assert has_minimum_role(UserRole.ADMIN, UserRole.VIEWER) is True

    # MANAGER checks
    assert has_minimum_role(UserRole.MANAGER, UserRole.ADMIN) is False
    assert has_minimum_role(UserRole.MANAGER, UserRole.MANAGER) is True
    assert has_minimum_role(UserRole.MANAGER, UserRole.STAFF) is True

    # VIEWER checks (lowest privilege)
    assert has_minimum_role(UserRole.VIEWER, UserRole.STAFF) is False
    assert has_minimum_role(UserRole.VIEWER, UserRole.VIEWER) is True

    # Invalid input handling
    assert has_minimum_role("invalid_role", UserRole.VIEWER) is False


# ==============================================================================
# 2. Tests for RoleChecker Dependency
# ==============================================================================
def test_role_checker_success():
    checker = RoleChecker(UserRole.MANAGER)
    mock_user = MagicMock(spec=User)
    mock_user.role = UserRole.ADMIN  # ADMIN exceeds MANAGER requirement
    mock_user.id = "user_123"

    # Should run without raising exception and return the user
    allowed_user = checker(mock_user)
    assert allowed_user == mock_user


def test_role_checker_denied():
    checker = RoleChecker(UserRole.ADMIN)
    mock_user = MagicMock(spec=User)
    mock_user.role = UserRole.MANAGER  # MANAGER is insufficient for ADMIN
    mock_user.id = "user_123"

    with pytest.raises(HTTPException) as exc:
        checker(mock_user)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Minimum role required: admin" in exc.value.detail


# ==============================================================================
# 3. Protected Route Integration Tests via TestClient
# ==============================================================================
@pytest.fixture(autouse=True)
def cleanup_dependency_overrides():
    # Make sure dependency overrides are cleared after each test
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_public_routes():
    client = TestClient(app)

    # /health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    # /ready endpoint
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_protected_me_route_unauthenticated():
    client = TestClient(app)

    # Requesting without authentication (middleware or get_current_user will reject)
    response = client.get("/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_me_route_authenticated():
    client = TestClient(app)

    # Define a mock authenticated user
    mock_user = User(
        clerk_id="user_clerk_me",
        email="me@example.com",
        first_name="Alice",
        last_name="Smith",
        role=UserRole.MANAGER,
        is_active=True
    )
    mock_user.id = "mock-uuid-123"

    # Override the get_current_user dependency
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Mock AuthMiddleware token verification to let it pass
    with patch("app.middleware.auth.authenticate_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {"sub": "user_clerk_me"}

        response = client.get("/users/me", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == 200

        data = response.json()
        assert data["clerk_id"] == "user_clerk_me"
        assert data["email"] == "me@example.com"
        assert data["role"] == "manager"


@pytest.mark.asyncio
async def test_role_protected_route_denied():
    client = TestClient(app)

    # Mock a VIEWER user
    mock_user = User(
        clerk_id="user_clerk_viewer",
        email="viewer@example.com",
        role=UserRole.VIEWER,
        is_active=True
    )
    mock_user.id = "mock-uuid-999"

    # Override get_current_user
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Mock AuthMiddleware to let it pass
    with patch("app.middleware.auth.authenticate_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {"sub": "user_clerk_viewer"}

        # /admin/system-status requires ADMIN role
        response = client.get("/admin/system-status", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == 403
        assert "Minimum role required: admin" in response.json()["detail"]


@pytest.mark.asyncio
async def test_role_protected_route_allowed():
    client = TestClient(app)

    # Mock an ADMIN user
    mock_user = User(
        clerk_id="user_clerk_admin",
        email="admin@example.com",
        role=UserRole.ADMIN,
        is_active=True
    )
    mock_user.id = "mock-uuid-admin"

    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Mock AuthMiddleware to let it pass
    with patch("app.middleware.auth.authenticate_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {"sub": "user_clerk_admin"}

        response = client.get("/admin/system-status", headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "operational"
        assert data["accessed_by"] == "admin@example.com"
        assert data["role"] == "admin"
