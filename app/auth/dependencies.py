
import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.clerk_client import clerk_client
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
        query = select(User).where(User.clerk_id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Database error loading current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed during profile check."
        )

    if user and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User profile not found or inactive."
        )

    if not user:
        # Clerk remains the identity source of truth.  Provision a local profile
        # only after the middleware has verified the Clerk JWT.
        try:
            profile = await clerk_client.get_user(user_id)
            emails = profile.get("email_addresses", [])
            primary = next((item.get("email_address") for item in emails if item.get("id") == profile.get("primary_email_address_id")), None)
            email = primary or (emails[0].get("email_address") if emails else None)
            if not email:
                raise ValueError("Clerk profile has no email")
            user = User(clerk_id=user_id, email=email, first_name=profile.get("first_name"), last_name=profile.get("last_name"), avatar_url=profile.get("image_url"))
            db.add(user)
            await db.flush()
        except Exception as exc:
            logger.error("Unable to provision authenticated Clerk user: %s", exc)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User profile not found or inactive.")

    return user
