import base64
import asyncio
import time
import logging
from typing import Dict, Any, Optional
import httpx
import jwt
from app.core.config import settings
from app.auth.exceptions import ConfigurationError, InvalidTokenError, TokenExpiredError

logger = logging.getLogger("app.auth.jwt")


def get_jwks_url_from_publishable_key(publishable_key: str) -> Optional[str]:
    """
    Derives the Clerk JWKS endpoint from the Publishable Key.
    Clerk publishable keys have the format: pk_test_Y2xlcmsuZXhhbXBsZS5jb20k or pk_live_Y2xlcmsuZXhhbXBsZS5jb20k
    Where the third part is base64url encoded.
    """
    if not publishable_key:
        return None
    try:
        parts = publishable_key.split("_")
        if len(parts) < 3:
            return None
        # The third part contains the base64url-encoded domain name ending with a '$'
        encoded_payload = parts[2]
        padding = len(encoded_payload) % 4
        if padding:
            encoded_payload += "=" * (4 - padding)

        # Use urlsafe_b64decode to properly handle base64url characters like - and _
        decoded = base64.urlsafe_b64decode(encoded_payload).decode("utf-8")
        domain = decoded.rstrip("$")
        if domain:
            return f"https://{domain}/.well-known/jwks.json"
    except Exception as e:
        logger.debug(f"Failed to derive JWKS URL from publishable key: {e}")
    return None


class JWKSKeyManager:
    """
    Thread-safe, async-aware cached JWKS manager.
    Fetches signing keys asynchronously from Clerk and caches them in memory.
    """
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
        self._keys: Dict[str, jwt.PyJWK] = {}
        self._expires_at: float = 0.0
        self._lock = asyncio.Lock()

    def get_jwks_url(self) -> str:
        """
        Resolves the JWKS URL using settings or publishable key fallback.
        """
        # 1. Use custom CLERK_JWKS_URL if configured
        if settings.CLERK_JWKS_URL:
            return settings.CLERK_JWKS_URL

        # 2. Derive JWKS URL from CLERK_PUBLISHABLE_KEY
        derived_url = get_jwks_url_from_publishable_key(settings.CLERK_PUBLISHABLE_KEY)
        if derived_url:
            return derived_url

        # 3. Fail with ConfigurationError if neither is configured
        raise ConfigurationError(
            "Clerk authentication configuration is incomplete. "
            "Please provide CLERK_JWKS_URL or CLERK_PUBLISHABLE_KEY."
        )

    async def fetch_jwks(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """
        Fetches the raw JWKS JSON from the Clerk endpoint.
        """
        jwks_url = self.get_jwks_url()
        headers = {}
        # If calling Clerk API backend JWKS, we may need authorization header
        if settings.CLERK_SECRET_KEY and "api.clerk.com" in jwks_url:
            headers["Authorization"] = f"Bearer {settings.CLERK_SECRET_KEY}"

        try:
            response = await client.get(jwks_url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching JWKS: {e.response.status_code} - {e.response.text}")
            raise ConfigurationError(f"Failed to fetch JWKS from Clerk: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Failed to fetch JWKS from Clerk: {e}")
            raise ConfigurationError(f"Failed to fetch JWKS from Clerk: {str(e)}")

    async def get_public_key(self, kid: str) -> jwt.PyJWK:
        """
        Returns the PyJWK public key for the given Key ID (kid).
        Uses a double-checked locking pattern with asyncio.Lock.
        """
        current_time = time.time()

        # Fast path: cached key is valid
        if kid in self._keys and current_time < self._expires_at:
            return self._keys[kid]

        # Slow path: acquire lock and refresh keys if needed
        async with self._lock:
            # Recheck condition once inside the lock
            if kid in self._keys and current_time < self._expires_at:
                return self._keys[kid]

            logger.info("JWKS cache expired or key not found. Refreshing keys from Clerk...")
            async with httpx.AsyncClient() as client:
                jwks_data = await self.fetch_jwks(client)

            try:
                jwk_set = jwt.PyJWKSet.from_dict(jwks_data)
                new_keys = {}
                for jwk in jwk_set.keys:
                    jwk_kid = jwk.key_id
                    if jwk_kid:
                        new_keys[jwk_kid] = jwk

                self._keys = new_keys
                self._expires_at = time.time() + self.cache_ttl
            except Exception as e:
                logger.error(f"Error parsing JWKS data: {e}")
                raise InvalidTokenError("Failed to parse signing keys from Clerk.")

            if kid not in self._keys:
                logger.error(f"Key ID '{kid}' not found in fetched JWKS keys.")
                raise InvalidTokenError("Invalid signing key ID.")

            return self._keys[kid]


# Singleton instance of the key manager
jwks_manager = JWKSKeyManager()


async def verify_clerk_token(token: str) -> Dict[str, Any]:
    """
    Decodes and verifies a Clerk JWT token.
    Validates token signature using Clerk's public keys, and verifies claims (exp, iss).

    Raises:
        InvalidTokenError: If signature, format, or claims are invalid.
        TokenExpiredError: If token has expired.
        ConfigurationError: If Clerk configuration is invalid.
    """
    if not token:
        raise InvalidTokenError("Token is empty")

    try:
        # Extract kid header from the token
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise InvalidTokenError("Token is missing the 'kid' header.")
    except Exception as e:
        raise InvalidTokenError(f"Invalid token format: {str(e)}")

    # Retrieve the public key
    pyjwk = await jwks_manager.get_public_key(kid)
    public_key = pyjwk.key

    # Retrieve expected issuer
    jwks_url = jwks_manager.get_jwks_url()
    # The issuer is the domain of the JWKS URL (e.g. https://clerk.example.com)
    expected_issuer = jwks_url.split("/.well-known")[0]

    try:
        # Verify and decode
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=expected_issuer,
            options={"verify_aud": False}  # Clerk session JWTs might not set 'aud' or it might match frontend
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError(str(e))
    except jwt.InvalidIssuerError as e:
        raise InvalidTokenError(f"Invalid issuer: {str(e)}")
    except jwt.InvalidSignatureError as e:
        raise InvalidTokenError(f"Invalid signature: {str(e)}")
    except jwt.PyJWTError as e:
        raise InvalidTokenError(str(e))
