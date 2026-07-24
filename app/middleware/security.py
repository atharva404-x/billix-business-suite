
import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

logger = logging.getLogger("app.middleware.security")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware injecting OWASP security headers on all outgoing HTTP responses.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Standard OWASP Security Headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"

        if settings.ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware limiting maximum allowed request payload size (Content-Length).
    Rejects requests exceeding MAX_REQUEST_SIZE_BYTES with HTTP 413 Payload Too Large.
    """

    def __init__(self, app, max_bytes: int = settings.MAX_REQUEST_SIZE_BYTES):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length_header = request.headers.get("Content-Length")

        if content_length_header:
            try:
                content_length = int(content_length_header)
                if content_length > self.max_bytes:
                    logger.warning(
                        "Payload too large reject: %d bytes exceeds max %d bytes",
                        content_length,
                        self.max_bytes
                    )
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Payload Too Large"}
                    )
            except ValueError:
                pass

        return await call_next(request)
