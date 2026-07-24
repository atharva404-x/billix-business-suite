
import logging

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

logger = logging.getLogger("app.middleware.error_handler")

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global Error Handling Middleware.
    Catches unhandled exceptions, logs structured error context, reports to Sentry,
    and returns a production-safe JSON response with request tracking details.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            # Let standard FastAPI HTTPExceptions pass through to FastAPI handlers
            raise
        except Exception as exc:
            request_id = getattr(request.state, "request_id", "unknown")
            correlation_id = getattr(request.state, "correlation_id", "unknown")

            logger.error(
                "Unhandled exception on %s %s [request_id=%s, correlation_id=%s]: %s",
                request.method,
                request.url.path,
                request_id,
                correlation_id,
                exc,
                exc_info=True
            )

            # Report exception to Sentry if available
            try:
                import sentry_sdk
                sentry_sdk.capture_exception(exc)
            except Exception:
                pass

            # In development, detail can include exception message; in production, keep generic
            detail_msg = str(exc) if settings.ENV == "development" else "Internal Server Error"

            return JSONResponse(
                status_code=500,
                content={
                    "detail": detail_msg,
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Correlation-ID": correlation_id,
                }
            )
