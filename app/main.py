from fastapi import FastAPI, Depends

from app.core.config import settings
from app.middleware.auth import AuthMiddleware
from app.api.v1.businesses import router as business_router
from app.auth.dependencies import get_current_user
from app.auth.role_helpers import RoleChecker
from app.models.user import User
from app.models.roles import UserRole

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Billix GST Billing, Inventory & Business Management SaaS API",
    version="1.0.0"
)

# Register API Routers
app.include_router(business_router, prefix="/api/v1")

# Configure the global AuthMiddleware
# Core metadata and health endpoints are designated as public (unauthenticated) paths
app.add_middleware(
    AuthMiddleware,
    public_paths={
        "/",
        "/health",
        "/ready",
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
async def readiness_check():
    """
    Public readiness check endpoint.
    """
    return {
        "status": "ready"
    }


@app.get("/users/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Protected route that retrieves the currently authenticated user's profile details.

    Requires valid Clerk JWT authentication via get_current_user dependency.
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

    Requires valid Clerk authentication AND a minimum role privilege of 'admin'.
    """
    return {
        "status": "operational",
        "accessed_by": admin_user.email,
        "role": admin_user.role
    }
