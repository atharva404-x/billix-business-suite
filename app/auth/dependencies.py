import logging
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User

logger = logging.getLogger("app.auth.dependencies")


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency to retrieve the currently authenticated user from the database.

    Extracts the Clerk user ID (sub) attached to the request state by AuthMiddleware,
    then loads the corresponding User object from the database.

    Raises:
        HTTPException (401): If the request is unauthenticated or the user profile is missing or inactive.
    """
    user_id: Optional[str] = getattr(request.state, "user_id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )

    # Query the user from the database by clerk_id
    try:
        query = select(User).where(User.clerk_id == user_id, User.is_active == True)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Database error loading current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed during profile check."
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user profile not found or inactive."
        )

    return user
