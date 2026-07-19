import pytest
from starlette.requests import Request
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.middleware.auth import AuthMiddleware
from app.auth.exceptions import TokenExpiredError, InvalidTokenError, MissingTokenError


# Create a mock FastAPI app for middleware testing
def create_test_app() -> FastAPI:
    app = FastAPI()

    # Register AuthMiddleware
    app.add_middleware(AuthMiddleware, public_paths={"/public", "/health"})

    @app.get("/public")
    def public_route():
        return {"status": "ok", "type": "public"}

    @app.get("/health")
    def health_route():
        return {"status": "healthy"}

    @app.get("/private")
    def private_route(request: Request):
        return {
            "status": "authorized",
            "user_id": getattr(request.state, "user_id", None),
            "user": getattr(request.state, "user", None)
        }

    return app


def test_public_route_no_auth():
    app = create_test_app()
    client = TestClient(app)

    # Request public path without any auth header
    response = client.get("/public")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "type": "public"}

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_private_route_missing_auth():
    app = create_test_app()
    client = TestClient(app)

    # Request private path without header
    response = client.get("/private")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authorization header is missing."}


def test_private_route_invalid_format():
    app = create_test_app()
    client = TestClient(app)

    # Request private path with malformed header
    response = client.get("/private", headers={"Authorization": "InvalidTokenFormat"})
    assert response.status_code == 401
    assert "Bearer" in response.json()["detail"]


@pytest.mark.asyncio
async def test_private_route_expired_token():
    app = create_test_app()
    client = TestClient(app)

    # Mock JWT verification to raise TokenExpiredError
    with patch("app.middleware.auth.authenticate_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.side_effect = TokenExpiredError("Token has expired")

        response = client.get("/private", headers={"Authorization": "Bearer expired_jwt"})
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_private_route_valid_token():
    app = create_test_app()
    client = TestClient(app)

    mock_payload = {
        "sub": "user_clerk_999",
        "email": "user@example.com",
        "first_name": "Jane"
    }

    # Mock authenticate_request to return mock verified payload
    with patch("app.middleware.auth.authenticate_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = mock_payload

        response = client.get("/private", headers={"Authorization": "Bearer valid_jwt"})
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "authorized"
        assert data["user_id"] == "user_clerk_999"
        assert data["user"]["email"] == "user@example.com"
        mock_auth.assert_called_once_with("Bearer valid_jwt")


@pytest.mark.asyncio
async def test_private_route_unexpected_error():
    app = create_test_app()
    client = TestClient(app)

    # Mock JWT verification to raise an unexpected Exception
    with patch("app.middleware.auth.authenticate_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.side_effect = Exception("System explosion")

        response = client.get("/private", headers={"Authorization": "Bearer boom"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Authentication failed"}
