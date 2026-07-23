import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import request_id_var, correlation_id_var
from app.core.metrics import metrics_collector


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware ensuring every request carries unique X-Request-ID and X-Correlation-ID.
    Attaches identifiers to request state, HTTP response headers, logging contextvars,
    and records request duration metrics.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract existing IDs from incoming headers or generate new UUIDs
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        correlation_id = request.headers.get("X-Correlation-ID") or request_id

        # Attach to request state
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        # Set logging context variables
        token_req = request_id_var.set(request_id)
        token_corr = correlation_id_var.set(correlation_id)

        start_time = time.time()
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Record request metrics
            metrics_collector.record_request(response.status_code, duration_ms)

            # Echo tracing headers back in response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            # Reset context variables for task safety
            request_id_var.reset(token_req)
            correlation_id_var.reset(token_corr)
