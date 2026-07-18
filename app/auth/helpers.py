import logging
from typing import Dict, Any, Optional
from app.auth.exceptions import MissingTokenError, InvalidTokenError
from app.auth.jwt_utils import verify_clerk_token

logger = logging.getLogger("app.auth.helpers")


def extract_token_from_header(authorization_header: Optional[str]) -> Optional[str]:
    """
    Extracts the Bearer token from the standard Authorization header.

    Args:
        authorization_header: The raw Authorization header string (e.g., 'Bearer <token>').

    Returns:
        The clean JWT token string, or None if the header is missing or malformed.
    """
    if not authorization_header:
        return None

    parts = authorization_header.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


async def authenticate_request(authorization_header: Optional[str]) -> Dict[str, Any]:
    """
    Extracts and verifies the Clerk JWT token from the Authorization header.
    This helper is highly reusable across API routers, dependencies, and middlewares.

    Args:
        authorization_header: The raw Authorization header string.

    Returns:
        The decoded and verified token payload (containing user ID, claims, etc.).

    Raises:
        MissingTokenError: If the Authorization header is missing.
        InvalidTokenError: If the header is malformed or token verification fails.
        TokenExpiredError: If the token is expired.
    """
    token = extract_token_from_header(authorization_header)
    if not token:
        if not authorization_header:
            raise MissingTokenError("Authorization header is missing.")
        else:
            raise InvalidTokenError("Authorization header must follow 'Bearer <token>' format.")

    # Verify and decode the token
    payload = await verify_clerk_token(token)
    return payload
