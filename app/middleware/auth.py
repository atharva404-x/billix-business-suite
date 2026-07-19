import logging
from typing import Set, Optional
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from app.auth.helpers import authenticate_request
from app.auth.exceptions import AuthError

logger = logging.getLogger("app.middleware.auth")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Enforces Clerk JWT authentication on all requests, except for designated public paths.

    Attaches the decoded token payload to `request.state.user` and `request.state.user_id` upon success.
    """
    def __init__(self, app, public_paths: Optional[Set[str]] = None):
        super().__init__(app)
        # Default core public endpoints for health checking and docs
        self.public_paths = public_paths or {
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/ready"
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # Pass through if path is public
        if path in self.public_paths or any(path.startswith(p) for p in self.public_paths if p != "/"):
            return await call_next(request)

        # Extract and verify Clerk JWT from Authorization header
        auth_header = request.headers.get("Authorization")

        try:
            # Reuses authenticate_request helper from app.auth.helpers
            payload = await authenticate_request(auth_header)

            # Attach authenticated identity details to request state
            request.state.user = payload
            request.state.user_id = payload.get("sub")

        except AuthError as e:
            logger.warning(f"AuthMiddleware authentication rejection: {e.message}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.message}
            )
        except Exception as e:
            logger.error(f"Unexpected error in AuthMiddleware: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication failed"}
            )

        return await call_next(request)
