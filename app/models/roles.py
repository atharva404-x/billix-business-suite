from enum import Enum
from typing import List


class UserRole(str, Enum):
    """
    Global system-level role attached to a User record.
    Used for platform-level access (e.g. super-admin operations).
    Per-business access is governed by BusinessRole on BusinessMember.
    """
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"


class BusinessRole(str, Enum):
    """
    Per-business membership role stored on BusinessMember.
    Governs what a user may do within a specific business tenant.
    """
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    SALES = "sales"
    INVENTORY = "inventory"
    VIEWER = "viewer"


# Hierarchy order for BusinessRole: index 0 = highest privilege.
BUSINESS_ROLE_ORDER: List[BusinessRole] = [
    BusinessRole.OWNER,
    BusinessRole.ADMIN,
    BusinessRole.MANAGER,
    BusinessRole.ACCOUNTANT,
    BusinessRole.SALES,
    BusinessRole.INVENTORY,
    BusinessRole.VIEWER,
]

# Legacy hierarchy kept for backward-compat with UserRole checks.
ROLE_ORDER: List[UserRole] = [
    UserRole.OWNER,
    UserRole.ADMIN,
    UserRole.MANAGER,
    UserRole.STAFF,
    UserRole.VIEWER,
]


def has_minimum_role(user_role: UserRole, required_role: UserRole) -> bool:
    """
    Returns True if user_role meets or exceeds required_role in the global hierarchy.
    """
    try:
        user_index = ROLE_ORDER.index(user_role)
        required_index = ROLE_ORDER.index(required_role)
        return user_index <= required_index
    except ValueError:
        return False


def has_minimum_business_role(
    member_role: BusinessRole, required_role: BusinessRole
) -> bool:
    """
    Returns True if member_role meets or exceeds required_role in the business hierarchy.
    """
    try:
        user_index = BUSINESS_ROLE_ORDER.index(member_role)
        required_index = BUSINESS_ROLE_ORDER.index(required_role)
        return user_index <= required_index
    except ValueError:
        return False
