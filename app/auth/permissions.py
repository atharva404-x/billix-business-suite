"""
RBAC permission system for Billix.

Architecture
------------
Permission  — granular action enum (e.g. INVOICE_CREATE)
ROLE_PERMISSIONS — maps every BusinessRole to its permitted set
PermissionChecker — FastAPI dependency factory; resolves business_id from
                    request path/query params, loads the caller's BusinessMember
                    record, and asserts the required Permission is present.
"""
import uuid
import logging
from enum import Enum
from typing import Set, Dict
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db_session
from app.models.user import User
from app.models.roles import BusinessRole
from app.repositories.business import BusinessMemberRepository

logger = logging.getLogger("app.auth.permissions")


# ---------------------------------------------------------------------------
# Permission Enum
# ---------------------------------------------------------------------------

class Permission(str, Enum):
    # Business profile
    BUSINESS_READ = "business:read"
    BUSINESS_UPDATE = "business:update"
    BUSINESS_DELETE = "business:delete"

    # Business settings & preferences
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"

    # Team membership
    MEMBER_READ = "member:read"
    MEMBER_INVITE = "member:invite"
    MEMBER_REMOVE = "member:remove"

    # Customers
    CUSTOMER_READ = "customer:read"
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_UPDATE = "customer:update"
    CUSTOMER_DELETE = "customer:delete"

    # Suppliers
    SUPPLIER_READ = "supplier:read"
    SUPPLIER_CREATE = "supplier:create"
    SUPPLIER_UPDATE = "supplier:update"
    SUPPLIER_DELETE = "supplier:delete"

    # Products / categories / units (catalogue)
    PRODUCT_READ = "product:read"
    PRODUCT_CREATE = "product:create"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"

    # Inventory
    INVENTORY_READ = "inventory:read"
    INVENTORY_WRITE = "inventory:write"

    # Invoices
    INVOICE_READ = "invoice:read"
    INVOICE_CREATE = "invoice:create"
    INVOICE_UPDATE = "invoice:update"
    INVOICE_CANCEL = "invoice:cancel"

    # Payments
    PAYMENT_READ = "payment:read"
    PAYMENT_CREATE = "payment:create"

    # Reports & analytics
    REPORT_READ = "report:read"

    # Notifications
    NOTIFICATION_READ = "notification:read"
    NOTIFICATION_CREATE = "notification:create"
    NOTIFICATION_UPDATE = "notification:update"

    # Backups
    BACKUP_READ = "backup:read"
    BACKUP_CREATE = "backup:create"
    BACKUP_DELETE = "backup:delete"


# ---------------------------------------------------------------------------
# Role → Permission mapping
# ---------------------------------------------------------------------------

_ALL: Set[Permission] = set(Permission)

ROLE_PERMISSIONS: Dict[BusinessRole, Set[Permission]] = {
    BusinessRole.OWNER: _ALL,

    BusinessRole.ADMIN: _ALL - {Permission.BUSINESS_DELETE},

    BusinessRole.MANAGER: {
        Permission.BUSINESS_READ,
        Permission.SETTINGS_READ,
        Permission.MEMBER_READ,
        Permission.CUSTOMER_READ,
        Permission.CUSTOMER_CREATE,
        Permission.CUSTOMER_UPDATE,
        Permission.CUSTOMER_DELETE,
        Permission.SUPPLIER_READ,
        Permission.SUPPLIER_CREATE,
        Permission.SUPPLIER_UPDATE,
        Permission.SUPPLIER_DELETE,
        Permission.PRODUCT_READ,
        Permission.PRODUCT_CREATE,
        Permission.PRODUCT_UPDATE,
        Permission.PRODUCT_DELETE,
        Permission.INVENTORY_READ,
        Permission.INVENTORY_WRITE,
        Permission.INVOICE_READ,
        Permission.INVOICE_CREATE,
        Permission.INVOICE_UPDATE,
        Permission.INVOICE_CANCEL,
        Permission.PAYMENT_READ,
        Permission.PAYMENT_CREATE,
        Permission.REPORT_READ,
        Permission.NOTIFICATION_READ,
        Permission.NOTIFICATION_CREATE,
        Permission.NOTIFICATION_UPDATE,
        Permission.BACKUP_READ,
        Permission.BACKUP_CREATE,
    },

    BusinessRole.ACCOUNTANT: {
        Permission.BUSINESS_READ,
        Permission.CUSTOMER_READ,
        Permission.SUPPLIER_READ,
        Permission.PRODUCT_READ,
        Permission.INVENTORY_READ,
        Permission.INVOICE_READ,
        Permission.INVOICE_CREATE,
        Permission.INVOICE_UPDATE,
        Permission.INVOICE_CANCEL,
        Permission.PAYMENT_READ,
        Permission.PAYMENT_CREATE,
        Permission.REPORT_READ,
        Permission.NOTIFICATION_READ,
        Permission.BACKUP_READ,
    },

    BusinessRole.SALES: {
        Permission.BUSINESS_READ,
        Permission.CUSTOMER_READ,
        Permission.CUSTOMER_CREATE,
        Permission.CUSTOMER_UPDATE,
        Permission.PRODUCT_READ,
        Permission.INVOICE_READ,
        Permission.INVOICE_CREATE,
        Permission.INVOICE_UPDATE,
        Permission.PAYMENT_READ,
        Permission.PAYMENT_CREATE,
        Permission.NOTIFICATION_READ,
    },

    BusinessRole.INVENTORY: {
        Permission.BUSINESS_READ,
        Permission.SUPPLIER_READ,
        Permission.SUPPLIER_CREATE,
        Permission.SUPPLIER_UPDATE,
        Permission.PRODUCT_READ,
        Permission.PRODUCT_CREATE,
        Permission.PRODUCT_UPDATE,
        Permission.INVENTORY_READ,
        Permission.INVENTORY_WRITE,
        Permission.NOTIFICATION_READ,
    },

    BusinessRole.VIEWER: {
        Permission.BUSINESS_READ,
        Permission.CUSTOMER_READ,
        Permission.SUPPLIER_READ,
        Permission.PRODUCT_READ,
        Permission.INVENTORY_READ,
        Permission.INVOICE_READ,
        Permission.PAYMENT_READ,
        Permission.REPORT_READ,
        Permission.NOTIFICATION_READ,
        Permission.BACKUP_READ,
    },
}


def role_has_permission(role: BusinessRole, permission: Permission) -> bool:
    """Return True if the given BusinessRole grants the requested Permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


# ---------------------------------------------------------------------------
# PermissionChecker — FastAPI dependency factory
# ---------------------------------------------------------------------------

class PermissionChecker:
    """
    FastAPI dependency that enforces a Permission for the calling user within
    a specific business tenant.

    Resolves ``business_id`` from the request path parameters first, then
    from query parameters, so it works with both routing styles used in this
    project (e.g. ``/{business_id}/settings`` and ``?business_id=...``).

    Usage::

        @router.post("/invoices")
        async def create_invoice(
            ...,
            _: User = Depends(PermissionChecker(Permission.INVOICE_CREATE)),
        ): ...
    """

    def __init__(self, permission: Permission) -> None:
        self.permission = permission

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ) -> User:
        business_id = self._resolve_business_id(request)

        member_repo = BusinessMemberRepository(session)
        membership = await member_repo.get_by_user_and_business(
            current_user.id, business_id
        )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this business.",
            )

        if not role_has_permission(membership.role, self.permission):
            logger.warning(
                "Permission denied: user=%s role=%s permission=%s business=%s",
                current_user.id,
                membership.role,
                self.permission,
                business_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Permission denied. Required: {self.permission.value}. "
                    f"Your role: {membership.role.value}."
                ),
            )

        return current_user

    @staticmethod
    def _resolve_business_id(request: Request) -> uuid.UUID:
        """Extract business_id from path params, falling back to query params."""
        raw = request.path_params.get("business_id") or request.query_params.get(
            "business_id"
        )
        if not raw:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="business_id is required.",
            )
        try:
            return uuid.UUID(str(raw))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid business_id format.",
            )
