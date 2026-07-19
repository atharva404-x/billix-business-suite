import base64
import time
from typing import Optional
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import jwt
import httpx

from app.core.config import settings
from app.auth.exceptions import (
    AuthError,
    ConfigurationError,
    TokenExpiredError,
    InvalidTokenError,
    MissingTokenError,
)
from app.auth.jwt_utils import (
    get_jwks_url_from_publishable_key,
    jwks_manager,
    verify_clerk_token,
    JWKSKeyManager,
)
from app.auth.clerk_client import ClerkClient, clerk_client
from app.auth.helpers import extract_token_from_header, authenticate_request


# --- Helper to generate base64url encoded int for JWK ---
def int_to_base64url(val: int) -> str:
    byte_len = (val.bit_length() + 7) // 8
    val_bytes = val.to_bytes(byte_len, byteorder="big")
    return base64.urlsafe_b64encode(val_bytes).decode("utf-8").rstrip("=")


# --- Test Fixture: Generate RSA Keypair and mock JWK/JWT ---
@pytest.fixture(scope="module")
def rsa_keypair():
    # Generate keypair
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Create JWK dict
    numbers = public_key.public_numbers()
    n_b64 = int_to_base64url(numbers.n)
    e_b64 = int_to_base64url(numbers.e)

    jwk_dict = {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": "mock_kid_123",
        "n": n_b64,
        "e": e_b64,
    }

    # Extract private key PEM for signing
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return {
        "private_pem": private_pem,
        "jwk_dict": jwk_dict,
        "kid": "mock_kid_123",
    }


# --- Mock HTTPX structures ---
class MockResponse:
    def __init__(self, status_code: int, json_data: dict, text: Optional[str] = None):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text or (str(json_data) if json_data else "")

    def json(self) -> dict:
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://api.clerk.com")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("Error", request=request, response=response)


class MockAsyncClient:
    def __init__(self, response: MockResponse):
        self.response = response
        self.last_url = None
        self.last_headers = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def get(self, url: str, headers: Optional[dict] = None, timeout: Optional[float] = None) -> MockResponse:
        self.last_url = url
        self.last_headers = headers
        return self.response


# ==============================================================================
# 1. Tests for get_jwks_url_from_publishable_key
# ==============================================================================
def test_get_jwks_url_from_publishable_key():
    # Valid test key: pk_test_YWN0aXZlLXNoZXBoZXJkLTc1LmNsZXJrLmFjY291bnRzLmRldiQ
    # Decodes to active-shepherd-75.clerk.accounts.dev$
    key = "pk_test_YWN0aXZlLXNoZXBoZXJkLTc1LmNsZXJrLmFjY291bnRzLmRldiQ"
    url = get_jwks_url_from_publishable_key(key)
    assert url == "https://active-shepherd-75.clerk.accounts.dev/.well-known/jwks.json"

    # Empty key
    assert get_jwks_url_from_publishable_key("") is None

    # Invalid structure key
    assert get_jwks_url_from_publishable_key("pk_test_invalid") is None


# ==============================================================================
# 2. Tests for JWKSKeyManager settings and resolution
# ==============================================================================
def test_jwks_key_manager_get_url():
    manager = JWKSKeyManager()

    # Reset settings mock-like
    with patch.object(settings, "CLERK_JWKS_URL", "https://custom.jwks.url"):
        assert manager.get_jwks_url() == "https://custom.jwks.url"

    with patch.object(settings, "CLERK_JWKS_URL", ""), \
         patch.object(settings, "CLERK_PUBLISHABLE_KEY", "pk_test_YWN0aXZlLXNoZXBoZXJkLTc1LmNsZXJrLmFjY291bnRzLmRldiQ"):
        assert manager.get_jwks_url() == "https://active-shepherd-75.clerk.accounts.dev/.well-known/jwks.json"

    with patch.object(settings, "CLERK_JWKS_URL", ""), \
         patch.object(settings, "CLERK_PUBLISHABLE_KEY", ""):
        with pytest.raises(ConfigurationError):
            manager.get_jwks_url()


# ==============================================================================
# 3. Tests for JWKSKeyManager caching and fetching
# ==============================================================================
@pytest.mark.asyncio
async def test_jwks_key_manager_caching_and_fetching(rsa_keypair):
    manager = JWKSKeyManager(cache_ttl=2)  # Short TTL of 2 seconds for test

    # Define mock response payload
    jwks_payload = {"keys": [rsa_keypair["jwk_dict"]]}
    mock_response = MockResponse(200, jwks_payload)
    mock_client = MockAsyncClient(mock_response)

    # Patch httpx.AsyncClient to return our mock client
    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch.object(settings, "CLERK_JWKS_URL", "https://mock.clerk.com/jwks"):

        # 1. Fetch public key (should fetch from Clerk and cache it)
        pyjwk = await manager.get_public_key(rsa_keypair["kid"])
        assert pyjwk.key_id == rsa_keypair["kid"]
        assert len(manager._keys) == 1

        # 2. Fetch again immediately (should hit cache - no httpx client should be initialized)
        with patch("httpx.AsyncClient") as mock_http_init:
            pyjwk_cached = await manager.get_public_key(rsa_keypair["kid"])
            assert pyjwk_cached == pyjwk
            mock_http_init.assert_not_called()

        # 3. Request a non-existent kid
        with pytest.raises(InvalidTokenError) as exc:
            await manager.get_public_key("non_existent_kid")
        assert "Invalid signing key ID" in str(exc.value)


# ==============================================================================
# 4. Tests for verify_clerk_token
# ==============================================================================
@pytest.mark.asyncio
async def test_verify_clerk_token_success(rsa_keypair):
    # Generate valid JWT signed with the mock RSA key
    now = int(time.time())
    payload = {
        "sub": "user_123",
        "iss": "https://active-shepherd-75.clerk.accounts.dev",
        "exp": now + 3600,
        "nbf": now - 60,
        "iat": now,
    }

    headers = {"kid": rsa_keypair["kid"]}
    token = jwt.encode(payload, rsa_keypair["private_pem"], algorithm="RS256", headers=headers)

    # Mock get_public_key on the global jwks_manager
    jwk_obj = jwt.PyJWK(rsa_keypair["jwk_dict"])

    with patch.object(jwks_manager, "get_public_key", return_value=jwk_obj), \
         patch.object(jwks_manager, "get_jwks_url", return_value="https://active-shepherd-75.clerk.accounts.dev/.well-known/jwks.json"):

        verified_payload = await verify_clerk_token(token)
        assert verified_payload["sub"] == "user_123"
        assert verified_payload["iss"] == "https://active-shepherd-75.clerk.accounts.dev"


@pytest.mark.asyncio
async def test_verify_clerk_token_expired(rsa_keypair):
    # Generate expired JWT
    now = int(time.time())
    payload = {
        "sub": "user_123",
        "iss": "https://active-shepherd-75.clerk.accounts.dev",
        "exp": now - 3600,  # Expired 1 hour ago
        "iat": now - 7200,
    }
    headers = {"kid": rsa_keypair["kid"]}
    token = jwt.encode(payload, rsa_keypair["private_pem"], algorithm="RS256", headers=headers)

    jwk_obj = jwt.PyJWK(rsa_keypair["jwk_dict"])

    with patch.object(jwks_manager, "get_public_key", return_value=jwk_obj), \
         patch.object(jwks_manager, "get_jwks_url", return_value="https://active-shepherd-75.clerk.accounts.dev/.well-known/jwks.json"):

        with pytest.raises(TokenExpiredError):
            await verify_clerk_token(token)


@pytest.mark.asyncio
async def test_verify_clerk_token_invalid_issuer(rsa_keypair):
    now = int(time.time())
    payload = {
        "sub": "user_123",
        "iss": "https://wrong-issuer.com",  # Wrong issuer
        "exp": now + 3600,
    }
    headers = {"kid": rsa_keypair["kid"]}
    token = jwt.encode(payload, rsa_keypair["private_pem"], algorithm="RS256", headers=headers)

    jwk_obj = jwt.PyJWK(rsa_keypair["jwk_dict"])

    with patch.object(jwks_manager, "get_public_key", return_value=jwk_obj), \
         patch.object(jwks_manager, "get_jwks_url", return_value="https://active-shepherd-75.clerk.accounts.dev/.well-known/jwks.json"):

        with pytest.raises(InvalidTokenError) as exc:
            await verify_clerk_token(token)
        assert "Invalid issuer" in str(exc.value)


@pytest.mark.asyncio
async def test_verify_clerk_token_invalid_signature(rsa_keypair):
    # Generate another RSA key to sign but verify using the original key
    wrong_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    wrong_private_pem = wrong_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    now = int(time.time())
    payload = {
        "sub": "user_123",
        "iss": "https://active-shepherd-75.clerk.accounts.dev",
        "exp": now + 3600,
    }
    headers = {"kid": rsa_keypair["kid"]}
    token = jwt.encode(payload, wrong_private_pem, algorithm="RS256", headers=headers)

    jwk_obj = jwt.PyJWK(rsa_keypair["jwk_dict"])

    with patch.object(jwks_manager, "get_public_key", return_value=jwk_obj), \
         patch.object(jwks_manager, "get_jwks_url", return_value="https://active-shepherd-75.clerk.accounts.dev/.well-known/jwks.json"):

        with pytest.raises(InvalidTokenError) as exc:
            await verify_clerk_token(token)
        assert "Invalid signature" in str(exc.value)


@pytest.mark.asyncio
async def test_verify_clerk_token_missing_kid():
    token = jwt.encode({"sub": "user_123"}, "secret", algorithm="HS256")  # No kid header

    with pytest.raises(InvalidTokenError) as exc:
        await verify_clerk_token(token)
    assert "missing the 'kid' header" in str(exc.value)


# ==============================================================================
# 5. Tests for extract_token_from_header
# ==============================================================================
def test_extract_token_from_header():
    # Valid standard Bearer format
    assert extract_token_from_header("Bearer token123") == "token123"

    # Mixed casing on Bearer
    assert extract_token_from_header("bearer token123") == "token123"
    assert extract_token_from_header("BEARER token123") == "token123"

    # Whitespace cleanup
    assert extract_token_from_header("  Bearer  token123  ") == "token123"

    # Empty and None values
    assert extract_token_from_header(None) is None
    assert extract_token_from_header("") is None

    # Invalid layout
    assert extract_token_from_header("Bearer") is None
    assert extract_token_from_header("Token token123") is None
    assert extract_token_from_header("Bearer token123 extra") is None


# ==============================================================================
# 6. Tests for authenticate_request helper
# ==============================================================================
@pytest.mark.asyncio
async def test_authenticate_request_success():
    mock_payload = {"sub": "user_456", "iss": "clerk"}

    with patch("app.auth.helpers.verify_clerk_token", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = mock_payload

        payload = await authenticate_request("Bearer test_token")
        assert payload == mock_payload
        mock_verify.assert_called_once_with("test_token")


@pytest.mark.asyncio
async def test_authenticate_request_failures():
    # Missing header
    with pytest.raises(MissingTokenError):
        await authenticate_request(None)

    # Malformed format
    with pytest.raises(InvalidTokenError) as exc:
        await authenticate_request("InvalidTokenFormat")
    assert "format" in str(exc.value)


# ==============================================================================
# 7. Tests for ClerkClient API interactions
# ==============================================================================
@pytest.mark.asyncio
async def test_clerk_client_get_user_success():
    client = ClerkClient(secret_key="sk_test_mock_secret", api_url="https://api.clerk.test/v1")

    mock_user_data = {
        "id": "user_2X_test",
        "first_name": "John",
        "last_name": "Doe",
        "email_addresses": [{"email_address": "john.doe@example.com"}],
    }

    mock_resp = MockResponse(200, mock_user_data)
    mock_client = MockAsyncClient(mock_resp)

    with patch("httpx.AsyncClient", return_value=mock_client):
        user_profile = await client.get_user("user_2X_test")

        assert user_profile == mock_user_data
        assert mock_client.last_url == "https://api.clerk.test/v1/users/user_2X_test"
        assert mock_client.last_headers["Authorization"] == "Bearer sk_test_mock_secret"


@pytest.mark.asyncio
async def test_clerk_client_get_user_not_found():
    client = ClerkClient(secret_key="sk_test_mock_secret", api_url="https://api.clerk.test/v1")

    mock_resp = MockResponse(404, {"error": "User not found"})
    mock_client = MockAsyncClient(mock_resp)

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AuthError) as exc:
            await client.get_user("user_nonexistent")
        assert exc.value.status_code == 404
        assert "not found" in str(exc.value)


@pytest.mark.asyncio
async def test_clerk_client_get_user_unauthorized():
    client = ClerkClient(secret_key="sk_test_invalid", api_url="https://api.clerk.test/v1")

    mock_resp = MockResponse(401, {"error": "Unauthorized"})
    mock_client = MockAsyncClient(mock_resp)

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(ConfigurationError) as exc:
            await client.get_user("user_2X_test")
        assert "Secret Key is invalid" in str(exc.value)


@pytest.mark.asyncio
async def test_clerk_client_missing_secret_key():
    client = ClerkClient(secret_key="", api_url="https://api.clerk.test/v1")

    with pytest.raises(ConfigurationError) as exc:
        await client.get_user("user_123")
    assert "CLERK_SECRET_KEY is missing" in str(exc.value)
