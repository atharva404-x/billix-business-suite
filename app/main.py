import logging
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.sentry import init_sentry
from app.core.metrics import metrics_collector
from app.core.database import get_db_session
from app.middleware.auth import AuthMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.auth.dependencies import get_current_user
from app.auth.role_helpers import RoleChecker
from app.models.user import User
from app.models.roles import UserRole
from app.api import api_router

# Setup structured logging and initialize Sentry error reporting
setup_logging()
init_sentry()

logger = logging.getLogger("app.main")

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Billix GST Billing, Inventory & Business Management SaaS API",
    version="1.0.0"
)

# Register Reliability and Auth Middlewares (outermost first)
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
