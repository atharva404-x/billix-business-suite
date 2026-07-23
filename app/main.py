import logging
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.sentry import init_sentry
from app.core.metrics import metrics_collector
from app.core.database import get_db_session
from app.middleware.auth import AuthMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.security import SecurityHeadersMiddleware, RequestSizeLimitMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.auth.dependencies import get_current_user
from app.auth.role_helpers import RoleChecker
from app.models.user import User
from app.models.roles import UserRole
from app.api import api_router

# Setup structured logging and initialize Sentry error reporting
setup_logging()
init_sentry()

from fastapi.openapi.utils import get_openapi

logger = logging.getLogger("app.main")

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Billix GST Billing, Inventory & Business Management SaaS API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


def custom_openapi():
    """
    Custom OpenAPI schema generator configuring Clerk HTTP Bearer JWT security schemes.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description=(
            "Production API for Billix — GST Billing, Inventory & Business Management SaaS.\n\n"
            "**Authentication**: Requests require a valid Clerk Bearer JWT token in the `Authorization` header."
        ),
        routes=app.routes,
    )

    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "ClerkBearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter Clerk JWT token (Bearer <token>)",
        }
    }

    # Apply global security scheme for endpoints requiring authentication
    openapi_schema["security"] = [{"ClerkBearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Middleware Pipeline Assembly (Registered outermost to innermost)
# Outermost middlewares execute first on requests and last on responses
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Correlation-ID"],
    expose_headers=["X-Request-ID", "X-Correlation-ID"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestSizeLimitMiddleware, max_bytes=settings.MAX_REQUEST_SIZE_BYTES)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    AuthMiddleware,
    public_paths={
        "/",
        "/health",
        "/ready",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json"
    }
)


@app.get("/health")
async def health_check():
    """
    Public health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "env": settings.ENV
    }


@app.get("/ready")
async def readiness_check(session: AsyncSession = Depends(get_db_session)):
    """
    Public readiness check endpoint verifying database connectivity.
    """
    try:
        await session.execute(select(1))
        return {
            "status": "ready",
            "database": "connected"
        }
    except Exception as exc:
        logger.error("Readiness check failed - database disconnected: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "database": "disconnected"
            }
        )


@app.get("/metrics")
async def metrics():
    """
    Public metrics endpoint for application monitoring and metrics scraping.
    """
    return metrics_collector.get_summary()


@app.get("/users/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Protected route that retrieves the currently authenticated user's profile details.
    """
    return {
        "id": str(current_user.id),
        "clerk_id": current_user.clerk_id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
        "is_active": current_user.is_active
    }


@app.get("/admin/system-status")
async def get_admin_status(admin_user: User = Depends(RoleChecker(UserRole.ADMIN))):
    """
    Protected and Role-restricted route retrieving system operational status.
    """
    return {
        "status": "operational",
        "accessed_by": admin_user.email,
        "role": admin_user.role
    }


# Include all API routes
app.include_router(api_router, prefix="/api")
