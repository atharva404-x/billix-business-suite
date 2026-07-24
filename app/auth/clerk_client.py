
import logging
from typing import Any, Dict, Optional

import httpx

from app.auth.exceptions import AuthError, ConfigurationError
from app.core.config import settings

logger = logging.getLogger("app.auth.clerk_client")

class ClerkClient:
    """
    An async client for interacting with the Clerk Backend API.
    Used for retrieving user profiles and other identity operations.
    """
    def __init__(self, secret_key: Optional[str] = None, api_url: Optional[str] = None):
        self.secret_key = secret_key if secret_key is not None else settings.CLERK_SECRET_KEY
        self.api_url = (api_url or settings.CLERK_API_URL).rstrip("/")

    def _get_headers(self) -> Dict[str, str]:
        if not self.secret_key:
            raise ConfigurationError("Clerk authentication configuration is incomplete. CLERK_SECRET_KEY is missing.")
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves user details from Clerk Backend API (GET /v1/users/{user_id}).

        Args:
            user_id: The Clerk User ID (e.g., user_2X...).

        Returns:
            The user data dictionary.

        Raises:
            ConfigurationError: If the Clerk Secret Key is missing or invalid.
            AuthError: If the request fails, user is not found, or there's a network issue.
        """
        if not user_id:
            raise AuthError("User ID must be provided", status_code=400)

        headers = self._get_headers()
        url = f"{self.api_url}/users/{user_id}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=10.0)

                if response.status_code == 404:
                    logger.warning(f"User {user_id} not found in Clerk.")
                    raise AuthError(f"Clerk user not found: {user_id}", status_code=404)
                elif response.status_code in (401, 403):
                    logger.error(f"Clerk API authentication failed (401/403): {response.text}")
                    raise ConfigurationError("Clerk Secret Key is invalid or unauthorized.")

                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error calling Clerk: {e.response.status_code} - {e.response.text}")
                raise AuthError(f"Clerk API request failed: {e.response.status_code}", status_code=e.response.status_code)
            except httpx.RequestError as e:
                logger.error(f"Network error calling Clerk: {e}")
                raise AuthError(f"Network error contacting Clerk API: {str(e)}", status_code=502)

# Singleton instance of ClerkClient
clerk_client = ClerkClient()
