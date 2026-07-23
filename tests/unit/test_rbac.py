"""
Tests for the Billix RBAC system.

Covers:
- BusinessRole enum values
- Permission enum values
- ROLE_PERMISSIONS mapping completeness and correctness
- role_has_permission helper
- PermissionChecker dependency (allowed, denied, non-member, missing business_id)
"""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status

from app.models.roles import BusinessRole, has_minimum_business_role, BUSINESS_ROLE_ORDER
from app.auth.permissions import (
    Permission,
    ROLE_PERMISSIONS,
    PermissionChecker,
    role_has_permission,
)


# ==============================================================================
# 1. BusinessRole enum
# ==============================================================================

def test_business_role_values():
    assert BusinessRole.OWNER == "owner"
    assert BusinessRole.ADMIN == "admin"
    assert BusinessRole.MANAGER == "manager"
    assert BusinessRole.ACCOUNTANT == "accountant"
    assert BusinessRole.SALES == "sales"
    assert BusinessRole.INVENTORY == "inventory"
    assert BusinessRole.VIEWER == "viewer"


def test_business_role_order_completeness():
    """Every BusinessRole must appear in the hierarchy list exactly once."""
    assert set(BUSINESS_ROLE_ORDER) == set(BusinessRole)
    assert len(BUSINESS_ROLE_ORDER) == len(BusinessRole)


def test_has_minimum_business_role_owner_beats_all():
    for role in BusinessRole:
        assert has_minimum_business_role(BusinessRole.OWNER, role) is True


def test_has_minimum_business_role_viewer_beats_none_except_itself():
    for role in BusinessRole:
        if role != BusinessRole.VIEWER:
            assert has_minimum_business_role(BusinessRole.VIEWER, role) is False
    assert has_minimum_business_role(BusinessRole.VIEWER, BusinessRole.VIEWER) is True


def test_has_minimum_business_role_invalid():
    assert has_minimum_business_role("not_a_role", BusinessRole.VIEWER) is False


# ==============================================================================
# 2. Permission enum
# ==============================================================================

def test_permission_enum_has_all_domains():
    values = {p.value for p in Permission}
    assert "business:read" in values
    assert "business:delete" in values
    assert "settings:read" in values
    assert "settings:update" in values
    assert "customer:create" in values
    assert "customer:delete" in values
    assert "supplier:create" in values
    assert "product:create" in values
    assert "inventory:read" in values
    assert "inventory:write" in values
    assert "invoice:create" in values
    assert "invoice:cancel" in values
    assert "payment:create" in values
    assert "report:read" in values


# ==============================================================================
# 3. ROLE_PERMISSIONS mapping
# ==============================================================================

def test_role_permissions_covers_all_roles():
    """Every BusinessRole must have an entry in ROLE_PERMISSIONS."""
    for role in BusinessRole:
        assert role in ROLE_PERMISSIONS, f"{role} missing from ROLE_PERMISSIONS"


def test_owner_has_all_permissions():
    assert ROLE_PERMISSIONS[BusinessRole.OWNER] == set(Permission)


def test_admin_lacks_business_delete():
    assert Permission.BUSINESS_DELETE not in ROLE_PERMISSIONS[BusinessRole.ADMIN]
    # Admin has all other permissions
    for p in Permission:
        if p != Permission.BUSINESS_DELETE:
            assert p in ROLE_PERMISSIONS[BusinessRole.ADMIN], f"Admin missing {p}"


def test_viewer_is_read_only():
    write_permissions = {
        Permission.BUSINESS_UPDATE,
        Permission.BUSINESS_DELETE,
        Permission.SETTINGS_UPDATE,
        Permission.MEMBER_INVITE,
        Permission.MEMBER_REMOVE,
        Permission.CUSTOMER_CREATE,
        Permission.CUSTOMER_UPDATE,
        Permission.CUSTOMER_DELETE,
        Permission.SUPPLIER_CREATE,
        Permission.SUPPLIER_UPDATE,
        Permission.SUPPLIER_DELETE,
        Permission.PRODUCT_CREATE,
        Permission.PRODUCT_UPDATE,
        Permission.PRODUCT_DELETE,
        Permission.INVENTORY_WRITE,
        Permission.INVOICE_CREATE,
        Permission.INVOICE_UPDATE,
        Permission.INVOICE_CANCEL,
        Permission.PAYMENT_CREATE,
    }
    viewer_perms = ROLE_PERMISSIONS[BusinessRole.VIEWER]
    for p in write_permissions:
        assert p not in viewer_perms, f"Viewer should not have {p}"


def test_sales_cannot_manage_inventory():
    sales_perms = ROLE_PERMISSIONS[BusinessRole.SALES]
    assert Permission.INVENTORY_WRITE not in sales_perms
    assert Permission.SUPPLIER_CREATE not in sales_perms
    assert Permission.PRODUCT_CREATE not in sales_perms


def test_inventory_cannot_access_invoices_or_financials():
    inv_perms = ROLE_PERMISSIONS[BusinessRole.INVENTORY]
    assert Permission.INVOICE_CREATE not in inv_perms
    assert Permission.INVOICE_READ not in inv_perms
    assert Permission.PAYMENT_CREATE not in inv_perms
    assert Permission.REPORT_READ not in inv_perms


def test_accountant_can_invoice_and_pay_but_not_manage_products():
    acc_perms = ROLE_PERMISSIONS[BusinessRole.ACCOUNTANT]
    assert Permission.INVOICE_CREATE in acc_perms
    assert Permission.INVOICE_CANCEL in acc_perms
    assert Permission.PAYMENT_CREATE in acc_perms
    assert Permission.REPORT_READ in acc_perms
    assert Permission.PRODUCT_CREATE not in acc_perms
    assert Permission.INVENTORY_WRITE not in acc_perms


def test_privilege_monotonicity():
    """
    A role higher in the hierarchy must never have fewer permissions than a
    lower-ranked role (with the sole exception of BUSINESS_DELETE for ADMIN).
    """
    owner = ROLE_PERMISSIONS[BusinessRole.OWNER]
    admin = ROLE_PERMISSIONS[BusinessRole.ADMIN]
    manager = ROLE_PERMISSIONS[BusinessRole.MANAGER]

    # Admin ⊆ Owner
    assert admin.issubset(owner)
    # Manager ⊆ Admin
    assert manager.issubset(admin)


# ==============================================================================
# 4. role_has_permission helper
# ==============================================================================

def test_role_has_permission_true():
    assert role_has_permission(BusinessRole.OWNER, Permission.BUSINESS_DELETE) is True
    assert role_has_permission(BusinessRole.SALES, Permission.INVOICE_CREATE) is True
    assert role_has_permission(BusinessRole.INVENTORY, Permission.INVENTORY_WRITE) is True


def test_role_has_permission_false():
    assert role_has_permission(BusinessRole.VIEWER, Permission.INVOICE_CREATE) is False
    assert role_has_permission(BusinessRole.SALES, Permission.INVENTORY_WRITE) is False
    assert role_has_permission(BusinessRole.ACCOUNTANT, Permission.PRODUCT_CREATE) is False


def test_role_has_permission_unknown_role():
    assert role_has_permission("ghost", Permission.BUSINESS_READ) is False


# ==============================================================================
# 5. PermissionChecker dependency
# ==============================================================================

def _make_request(business_id: uuid.UUID = None, use_path: bool = True) -> MagicMock:
    """Build a minimal mock Request for PermissionChecker."""
    req = MagicMock()
    bid_str = str(business_id) if business_id else None
    if use_path:
        req.path_params = {"business_id": bid_str} if bid_str else {}
        req.query_params = {}
    else:
        req.path_params = {}
        req.query_params = {"business_id": bid_str} if bid_str else {}
    return req


def _make_user(user_id: uuid.UUID = None) -> MagicMock:
    user = MagicMock()
    user.id = user_id or uuid.uuid4()
    return user


def _make_membership(role: BusinessRole) -> MagicMock:
    m = MagicMock()
    m.role = role
    return m


@pytest.mark.asyncio
async def test_permission_checker_allowed_path_param():
    bid = uuid.uuid4()
    user = _make_user()
    membership = _make_membership(BusinessRole.MANAGER)

    checker = PermissionChecker(Permission.INVOICE_CREATE)
    request = _make_request(business_id=bid, use_path=True)

    mock_repo = AsyncMock()
    mock_repo.get_by_user_and_business.return_value = membership

    with patch(
        "app.auth.permissions.BusinessMemberRepository",
        return_value=mock_repo
    ):
        result = await checker(request, current_user=user, session=AsyncMock())

    assert result is user
    mock_repo.get_by_user_and_business.assert_awaited_once_with(user.id, bid)


@pytest.mark.asyncio
async def test_permission_checker_allowed_query_param():
    bid = uuid.uuid4()
    user = _make_user()
    membership = _make_membership(BusinessRole.OWNER)

    checker = PermissionChecker(Permission.BUSINESS_DELETE)
    request = _make_request(business_id=bid, use_path=False)

    mock_repo = AsyncMock()
    mock_repo.get_by_user_and_business.return_value = membership

    with patch("app.auth.permissions.BusinessMemberRepository", return_value=mock_repo):
        result = await checker(request, current_user=user, session=AsyncMock())

    assert result is user


@pytest.mark.asyncio
async def test_permission_checker_denied_insufficient_role():
    bid = uuid.uuid4()
    user = _make_user()
    membership = _make_membership(BusinessRole.VIEWER)

    checker = PermissionChecker(Permission.INVOICE_CREATE)
    request = _make_request(business_id=bid, use_path=True)

    mock_repo = AsyncMock()
    mock_repo.get_by_user_and_business.return_value = membership

    with patch("app.auth.permissions.BusinessMemberRepository", return_value=mock_repo):
        with pytest.raises(HTTPException) as exc:
            await checker(request, current_user=user, session=AsyncMock())

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "invoice:create" in exc.value.detail


@pytest.mark.asyncio
async def test_permission_checker_non_member_raises_403():
    bid = uuid.uuid4()
    user = _make_user()

    checker = PermissionChecker(Permission.CUSTOMER_READ)
    request = _make_request(business_id=bid, use_path=True)

    mock_repo = AsyncMock()
    mock_repo.get_by_user_and_business.return_value = None  # not a member

    with patch("app.auth.permissions.BusinessMemberRepository", return_value=mock_repo):
        with pytest.raises(HTTPException) as exc:
            await checker(request, current_user=user, session=AsyncMock())

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "not a member" in exc.value.detail


@pytest.mark.asyncio
async def test_permission_checker_missing_business_id_raises_400():
    user = _make_user()

    checker = PermissionChecker(Permission.CUSTOMER_READ)
    # No business_id in path or query
    request = _make_request(business_id=None, use_path=True)

    with pytest.raises(HTTPException) as exc:
        await checker(request, current_user=user, session=AsyncMock())

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_permission_checker_invalid_business_id_raises_400():
    user = _make_user()

    checker = PermissionChecker(Permission.CUSTOMER_READ)
    req = MagicMock()
    req.path_params = {"business_id": "not-a-uuid"}
    req.query_params = {}

    with pytest.raises(HTTPException) as exc:
        await checker(req, current_user=user, session=AsyncMock())

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_permission_checker_inventory_role_allowed_for_stock_in():
    bid = uuid.uuid4()
    user = _make_user()
    membership = _make_membership(BusinessRole.INVENTORY)

    checker = PermissionChecker(Permission.INVENTORY_WRITE)
    request = _make_request(business_id=bid, use_path=False)

    mock_repo = AsyncMock()
    mock_repo.get_by_user_and_business.return_value = membership

    with patch("app.auth.permissions.BusinessMemberRepository", return_value=mock_repo):
        result = await checker(request, current_user=user, session=AsyncMock())

    assert result is user


@pytest.mark.asyncio
async def test_permission_checker_sales_denied_for_inventory_write():
    bid = uuid.uuid4()
    user = _make_user()
    membership = _make_membership(BusinessRole.SALES)

    checker = PermissionChecker(Permission.INVENTORY_WRITE)
    request = _make_request(business_id=bid, use_path=False)

    mock_repo = AsyncMock()
    mock_repo.get_by_user_and_business.return_value = membership

    with patch("app.auth.permissions.BusinessMemberRepository", return_value=mock_repo):
        with pytest.raises(HTTPException) as exc:
            await checker(request, current_user=user, session=AsyncMock())

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
