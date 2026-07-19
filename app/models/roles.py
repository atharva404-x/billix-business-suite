from enum import Enum
from typing import List


class UserRole(str, Enum):
    """
    Standard user roles supported in the Billix system.
    """
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"


# Defines the hierarchy order from most privileged to least privileged.
# Indexed from 0 (highest: OWNER) to 4 (lowest: VIEWER).
ROLE_ORDER: List[UserRole] = [
    UserRole.OWNER,
    UserRole.ADMIN,
    UserRole.MANAGER,
    UserRole.STAFF,
    UserRole.VIEWER
]


def has_minimum_role(user_role: UserRole, required_role: UserRole) -> bool:
    """
    Determines if user_role has sufficient privileges to meet or exceed required_role.

    Args:
        user_role: The role currently assigned to the user.
        required_role: The minimum role required for the operation.

    Returns:
        True if the user's role has equal or greater access than required_role, False otherwise.
    """
    try:
        user_index = ROLE_ORDER.index(user_role)
        required_index = ROLE_ORDER.index(required_role)
        # Higher privilege means lower list index (e.g., OWNER [index 0] <= VIEWER [index 4])
        return user_index <= required_index
    except ValueError:
        return False
