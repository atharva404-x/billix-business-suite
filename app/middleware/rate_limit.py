
import logging
import time
from typing import Dict, List, Set

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

logger = logging.getLogger("app.middleware.rate_limit")

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory sliding window rate limiting middleware per client IP address.
    Returns HTTP 429 Too Many Requests with Retry-After header when rate limit is exceeded.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = settings.RATE_LIMIT_PER_MINUTE,
        exempt_paths: Set[str] = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.exempt_paths = exempt_paths or {
            "/health",
            "/ready",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
        self.client_requests: Dict[str, List[float]] = {}

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address, checking X-Forwarded-For if available."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Exempt CORS preflight OPTIONS requests and designated health paths
        if request.method == "OPTIONS" or request.url.path in self.exempt_paths:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.time()

        # Retrieve request history and filter out timestamps outside sliding window
        history = self.client_requests.get(client_ip, [])
        cutoff = now - self.window_seconds
        history = [ts for ts in history if ts > cutoff]

        if len(history) >= self.requests_per_minute:
            logger.warning(
                "Rate limit exceeded for client IP %s (%d requests in 60s)",
                client_ip,
                len(history)
            )
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"},
                headers={"Retry-After": "60"}
            )

        history.append(now)
        self.client_requests[client_ip] = history

        return await call_next(request)
