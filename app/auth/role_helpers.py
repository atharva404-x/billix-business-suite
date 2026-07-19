import logging
from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.roles import UserRole, has_minimum_role

logger = logging.getLogger("app.auth.role_helpers")


class RoleChecker:
    """
    FastAPI dependency that enforces a minimum user role requirement.

    Verifies that the currently authenticated user possesses equal or higher role privilege
    than required, raising an HTTP 403 Forbidden exception if denied.
    """
    def __init__(self, required_role: UserRole):
        self.required_role = required_role

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not has_minimum_role(current_user.role, self.required_role):
            logger.warning(
                f"Role verification failed. User {current_user.id} has role '{current_user.role.value}', "
                f"but required minimum role is '{self.required_role.value}'."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Minimum role required: {self.required_role.value}"
            )
        return current_user
