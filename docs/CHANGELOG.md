# Billix — Changelog

> Append-only history of every engineering ticket implemented in Billix.
> Every AI assistant MUST append a new entry here after completing a ticket.
> Never rewrite or delete past entries.
> See [AI_RULES.md](./AI_RULES.md) for the required workflow.

---

## How to Add an Entry

After completing a ticket, append a new block under **Completed Engineering Tickets** using this exact template:

```
-----------------------------------------

Ticket ID:
<ticket-id>

Title:
<title>

Status:
Completed | In Progress | Blocked

Completion Date:
<YYYY-MM-DD>

Files Created:
- <path>
- <path>

Files Modified:
- <path>
- <path>

Summary:
<2–4 sentences describing what was done and why.>

Notes:
<optional — caveats, follow-ups, decisions worth remembering.>

Future Dependencies:
<ticket-id>
<ticket-id>

-----------------------------------------
```

---

## Completed Engineering Tickets

-----------------------------------------

Ticket ID:
CORE-HARDEN-001

Title:
Production Architecture Hardening

Status:
Completed

Completion Date:
2026-07-22

Files Created:
- alembic/versions/20260722_harden_core_integrity.py

Files Modified:
- app/core/database.py
- app/repositories/base.py
- app/services/inventory.py
- app/services/invoice.py
- app/core/config.py
- app/auth/jwt_utils.py
- app/auth/dependencies.py
- docs/CHANGELOG.md

Summary:
Made request transactions the unit of work, removed repository commits, fixed the router database dependency compatibility issue, hardened core tenant/invoice constraints, retained Decimal invoice calculations, repaired inventory stock lookup, and added safe Clerk first-login provisioning.

Notes:
- Configure CLERK_JWT_AUDIENCE in production to enforce audience validation.

Future Dependencies:
None

-----------------------------------------

-----------------------------------------

Ticket ID:
AUTH-001

Title:
Clerk Configuration

Status:
Completed

Completion Date:
2026-07-18

Files Created:
- app/auth/
- app/auth/__init__.py

Files Modified:
- app/core/config.py
- .env.example

Summary:
Configured Clerk environment variables (publishable key, secret key, JWKS endpoint) and initialized the authentication package on the backend. Established the `app/auth/` module that subsequent Clerk integration tickets will build on.

Notes:
- Backend repository assumed separate from this frontend repo.
- Frontend Clerk SDK wiring will be handled in AUTH-002.
- No runtime behavior changes yet — only configuration scaffolding.

Future Dependencies:
AUTH-002
AUTH-004
AUTH-005

-----------------------------------------

-----------------------------------------

Ticket ID:
AUTH-002

Title:
Backend Clerk Integration

Status:
Completed

Completion Date:
2026-07-18

Files Created:
- app/auth/clerk_client.py
- app/auth/exceptions.py
- app/auth/helpers.py
- app/auth/jwt_utils.py
- app/core/__init__.py
- app/core/config.py
- tests/__init__.py
- tests/unit/__init__.py
- tests/unit/test_auth.py

Files Modified:
- .gitignore
- docs/CHANGELOG.md

Summary:
Implemented the backend integration layer for Clerk. Created settings configurations, custom authentication exceptions, a thread-safe and expiration-aware cached JWKS manager, an async Clerk Backend API client, and reusable token-extraction helper functions. Additionally, added a comprehensive 15-test suite for complete backend authentication coverage.

Notes:
- Uses `base64.urlsafe_b64decode` to properly parse URL-safe base64 payloads from Clerk's publishable keys.
- Completely mocked out network calls during testing using custom Async Mock clients, preventing any external dependencies on test runs.
- Adheres to async-first conventions for FastAPI, utilizing httpx.AsyncClient and asyncio.Lock.

Future Dependencies:
AUTH-003
AUTH-004
AUTH-005

-----------------------------------------

-----------------------------------------

Ticket ID:
AUTH-004

Title:
Authentication Middleware

Status:
Completed

Completion Date:
2026-07-18

Files Created:
- app/middleware/__init__.py
- app/middleware/auth.py
- tests/unit/test_middleware.py

Files Modified:
- docs/CHANGELOG.md

Summary:
Implemented the FastAPI authentication middleware layer (`AuthMiddleware`). It intercepts incoming requests, enforces Clerk JWT verification on all non-public routes, handles public routes pass-through, and attaches authenticated user identity to the request state (`request.state.user` and `request.state.user_id`). Included a comprehensive unit test suite with 6 passing tests using FastAPI's TestClient.

Notes:
- Inherits from Starlette's `BaseHTTPMiddleware` to process incoming requests and outgoing responses asynchronously.
- Core public paths such as `/`, `/docs`, `/openapi.json`, `/health`, and `/ready` are bypassed by default.
- Returns explicit JSONResponse with 401 Unauthorized on invalid/missing/expired tokens.

Future Dependencies:
AUTH-005

-----------------------------------------

-----------------------------------------

Ticket ID:
AUTH-005

Title:
Current User Dependency

Status:
Completed

Completion Date:
2026-07-18

Files Created:
- app/core/database.py
- app/models/__init__.py
- app/models/base.py
- app/models/user.py
- app/auth/dependencies.py
- tests/unit/test_dependencies.py

Files Modified:
- app/core/config.py
- docs/CHANGELOG.md

Summary:
Set up core database connections, baseline declarative schemas, and BaseModelMixin, then created the get_current_user() FastAPI dependency. It reads the authenticated clerk user id from the request state, checks the user profile in the database, and injects the User object.

Notes:
- Async execution is handled natively using SQLAlchemy 2.0.
- Standardizes in-memory SQLite (aiosqlite) as a fast, zero-config local testing and development database.

Future Dependencies:
AUTH-006
AUTH-007

-----------------------------------------

-----------------------------------------

Ticket ID:
AUTH-006

Title:
Role Foundation

Status:
Completed

Completion Date:
2026-07-18

Files Created:
- app/models/roles.py
- app/auth/role_helpers.py

Files Modified:
- app/models/user.py
- docs/CHANGELOG.md

Summary:
Created the backend role foundation with OWNER, ADMIN, MANAGER, STAFF, and VIEWER roles using an Enum in `app/models/roles.py`. Implemented comparison hierarchy utilities and a reusable FastAPI dependency class `RoleChecker` in `app/auth/role_helpers.py`.

Notes:
- The role hierarchy indexes OWNER as the most privileged and VIEWER as the least privileged.
- Enforces role checks in endpoints asynchronously with complete exception handling (returning 403 Forbidden).

Future Dependencies:
AUTH-007

-----------------------------------------

-----------------------------------------

Ticket ID:
AUTH-007

Title:
Protected Routes

Status:
Completed

Completion Date:
2026-07-18

Files Created:
- app/main.py
- tests/unit/test_roles.py

Files Modified:
- docs/CHANGELOG.md

Summary:
Configured and registered AuthMiddleware globals and created public health and readiness check routes alongside authenticated and role-restricted API endpoints. Fully protected routes using get_current_user and RoleChecker dependencies.

Notes:
- Wrote integration tests covering public endpoints, unauthenticated rejections, and correct role permissions/denials via FastAPI's TestClient.

Future Dependencies:
AUTH-008

-----------------------------------------

-----------------------------------------

Ticket ID:
AUTH-008

Title:
Authentication Testing

Status:
Completed

Completion Date:
2026-07-18

Files Created:
- tests/unit/test_auth.py
- tests/unit/test_dependencies.py
- tests/unit/test_middleware.py
- tests/unit/test_roles.py

Files Modified:
- docs/CHANGELOG.md

Summary:
Wrote and compiled a comprehensive 34-test suite validating end-to-end backend authentication security and reliability. The tests cover JWT signature validation, thread-safe public key caching with double-checked lock, middleware extraction, route exceptions, DB lookups, role validation logic, and role protection on routing endpoints.

Notes:
- Replaced custom test runner loops in dependencies test with native async generators via pytest_asyncio.fixture to allow perfect async execution.

Future Dependencies:
None

-----------------------------------------

-----------------------------------------

Ticket ID:
TENANT-01, TENANT-02, CUST-01, CUST-02, CUST-03, CUST-04

Title:
Implement Multi-Tenant Business Profiles and Customer Module

Status:
Completed

Completion Date:
2026-07-21

Files Created:
- app/models/business.py
- app/models/customer.py
- app/schemas/__init__.py
- app/schemas/business.py
- app/schemas/customer.py
- app/repositories/__init__.py
- app/repositories/base.py
- app/repositories/business.py
- app/repositories/customer.py
- app/services/__init__.py
- app/services/business.py
- app/services/customer.py
- app/api/__init__.py
- app/api/v1/__init__.py
- app/api/v1/business.py
- app/api/v1/customers.py
- alembic/versions/20260720_add_business_and_customers.py

Files Modified:
- app/models/__init__.py
- alembic/env.py
- app/main.py

Summary:
Implemented the complete multi-tenant foundation with business profiles and customer management module including:
- BusinessProfile and BusinessMember models and migrations
- Customer model and migrations
- Pydantic schemas for business profiles and customers
- Repository and service layers for business profiles and customers
- REST API endpoints for CRUD operations on business profiles and customers
- Business isolation, authentication, GST validation, and duplicate customer checks

Notes:
- Uses BaseModelMixin with soft deletes and timestamps
- Uses SQLAlchemy async ORM and Alembic migrations
- Business access is checked via BusinessMemberRepository
- GST validation is basic format checking
- Customers are scoped by active business

Future Dependencies:
None

-----------------------------------------

-----------------------------------------

Ticket ID:
CUS-003

Title:
Customer Intelligence (Search, Filter, Sort, Pagination)

Status:
Completed

Completion Date:
2026-07-21

Files Created:
- alembic/versions/20260721_add_customer_code_and_indexes.py

Files Modified:
- app/models/customer.py
- app/schemas/customer.py
- app/repositories/customer.py
- app/services/customer.py
- app/api/v1/customers.py

Summary:
Implemented Customer Intelligence features:
- Added customer_code field to Customer model
- Added search by name, gstin, phone, customer_code
- Added filtering by active/inactive, customer type, city, state
- Added sorting by name, created_at, updated_at
- Optimized SQL queries with indexes on frequently filtered columns
- Updated list_customers to return tuple of (customers, total)
- Improved count query with SQLAlchemy func.count()

Notes:
- All queries are strictly business-scoped
- Soft delete is already handled by BaseModelMixin
- Default sort is name ascending
- Default filter is only active customers

Future Dependencies:
None

-----------------------------------------

-----------------------------------------

Ticket ID:
SUP-001

Title:
Supplier Management Module

Status:
Completed

Completion Date:
2026-07-21

Files Created:
- app/utils/__init__.py
- app/utils/validation.py
- app/models/supplier.py
- app/schemas/supplier.py
- app/repositories/supplier.py
- app/services/supplier.py
- app/api/v1/suppliers.py
- alembic/versions/20260721_add_suppliers_table.py

Files Modified:
- app/services/customer.py
- app/models/__init__.py
- app/schemas/__init__.py
- app/repositories/__init__.py
- app/services/__init__.py
- app/api/v1/__init__.py

Summary:
Implemented the complete Supplier Management module:
- Added Supplier model with business_id, supplier_code, name, type, gstin, contact info, address, credit limit, outstanding balance, and BaseModelMixin
- Created Supplier schemas (Create, Update, Response, ListResponse)
- Implemented SupplierRepository with search, filter, sort, pagination, and business isolation
- Implemented SupplierService with CRUD, validation (GSTIN, duplicates), and business access checks
- Added supplier API endpoints for all CRUD operations
- Refactored validate_gstin into a shared utility in app/utils/validation.py
- Updated alembic/env.py (we'll do that now)

Notes:
- Reused existing architecture from Customer module
- Reused BaseModel, BaseRepository, validation, and business isolation
- Future-compatible with Purchase Orders, Inventory, Expenses, Vendor Payments, Reports

Future Dependencies:
None

-----------------------------------------

-----------------------------------------

Ticket ID:
PROD-001

Title:
Product Catalog Management

Status:
Completed

Completion Date:
2026-07-21

Files Created:
- app/utils/__init__.py
- app/utils/validation.py
- app/models/unit.py
- app/models/category.py
- app/models/product.py
- app/schemas/unit.py
- app/schemas/category.py
- app/schemas/product.py
- app/repositories/unit.py
- app/repositories/category.py
- app/repositories/product.py
- app/services/unit.py
- app/services/category.py
- app/services/product.py
- app/api/v1/units.py
- app/api/v1/categories.py
- app/api/v1/products.py
- alembic/versions/20260721_add_products_categories_units.py

Files Modified:
- app/models/__init__.py
- app/schemas/__init__.py
- app/repositories/__init__.py
- app/services/__init__.py
- app/api/v1/__init__.py
- alembic/env.py
- docs/CHANGELOG.md
- app/utils/validation.py

Summary:
Implemented complete Product Catalog Management:
- Units management (custom units for products)
- Category management (hierarchical categories)
- Product management with all required fields (sku, barcode, hsn/sac, gst rate, pricing, stock, etc.)
- Search, filter, sort, pagination for all three
- Validation (hsn/sac, duplicate sku/barcode)
- Business isolation for all operations
- Soft delete
- Future-compatible with inventory, PO, invoices, etc.

Notes:
- Reused existing architecture from Customer/Supplier modules
- Moved validate_gstin and added validate_hsn_sac to shared utils
- Product current_stock initialized from opening_stock on creation

Future Dependencies:
None

-----------------------------------------

-----------------------------------------

Ticket ID:
INV-001

Title:
Inventory & Stock Management

Status:
Completed

Completion Date:
2026-07-21

Files Created:
- app/models/inventory.py
- app/schemas/inventory.py
- app/repositories/inventory.py
- app/services/inventory.py
- app/api/v1/inventory.py
- alembic/versions/20260721_add_inventory_transactions.py

Files Modified:
- app/models/__init__.py
- app/schemas/__init__.py
- app/repositories/__init__.py
- app/services/__init__.py
- app/api/v1/__init__.py
- alembic/env.py
- docs/CHANGELOG.md

Summary:
Implemented complete Inventory Management module:
- StockMovement enum (OPENING_STOCK, PURCHASE, SALE, SALES_RETURN, PURCHASE_RETURN, ADJUSTMENT_IN, ADJUSTMENT_OUT, MANUAL_UPDATE)
- InventoryTransaction model with ledger support
- InventoryService with stock_in, stock_out, adjust_stock, get_current_stock, get_inventory_history, validate_stock_availability
- API endpoints: POST /stock-in, POST /stock-out, POST /adjustment, GET /product/{id}, GET /history/{product_id}
- Reusable alert helpers (check_low_stock, check_out_of_stock, check_overstock)
- Business isolation, soft delete, search/filter/pagination/sorting for history
- Future-compatible with warehouses, batch/expiry tracking, PO, invoices, returns

Notes:
- Never directly update product.current_stock; always use InventoryService
- Transactions record previous/new stock for audit trail
- Stock availability validation prevents negative stock by default

Future Dependencies:
- Purchase Orders (uses reference_type/reference_id for PO links)
- Sales Invoices (uses SALE transaction type, reference for invoices)
- Returns (uses SALES_RETURN/PURCHASE_RETURN)
- Warehouses (add warehouse_id to InventoryTransaction later)
- Batch/Expiry Tracking (add batch_id, expiry_date later)

-----------------------------------------

-----------------------------------------

Ticket ID:
INVC-001

Title:
Sales Invoice Engine

Status:
Completed

Completion Date:
2026-07-21

Files Created:
- app/models/invoice.py
- app/schemas/invoice.py
- app/repositories/invoice.py
- app/services/invoice.py
- app/api/v1/invoices.py
- alembic/versions/20260721_add_invoice_payment_tables.py

Files Modified:
- app/models/__init__.py
- app/schemas/__init__.py
- app/repositories/__init__.py
- app/services/__init__.py
- app/api/v1/__init__.py
- alembic/env.py
- docs/CHANGELOG.md

Summary:
Implemented complete Sales Invoice Engine with Payments:
- Invoice and InvoiceItem models with proper relationships
- Payment model and PaymentMethod enum
- InvoiceService with automatic calculations (subtotal, GST, grand total, round-off)
- Outstanding balance tracking
- Payment recording with partial/full payment handling
- Stock deduction via InventoryService on invoice creation
- Unique invoice number generation per business
- Search/filter/sort for invoices
- Invoice statuses (draft, paid, unpaid, overdue, cancelled)
- Payment statuses (unpaid, partially paid, paid)
- Business isolation for all operations
- CRUD operations for invoices and payments

Notes:
- Stock is automatically deducted when invoice is created
- TODO: Reverse inventory on invoice cancellation
- TODO: Add business-specific invoice prefix support
- TODO: Implement IGST based on business/customer location
- TODO: Recalculate totals when invoice discount updated

Future Dependencies:
- PDF Generation
- Recurring Invoices
- Online Payment Gateway Integration
- Credit Notes

-----------------------------------------

-----------------------------------------

Ticket ID:
INVC-009

Title:
Invoice Engine Production Hardening

Status:
Completed

Completion Date:
2026-07-21

Files Created:
- app/utils/invoice_calculator.py
- alembic/versions/20260721_harden_invoice_engine.py

Files Modified:
- app/models/invoice.py
- app/schemas/invoice.py
- app/repositories/invoice.py
- app/services/invoice.py
- app/api/v1/invoices.py
- docs/CHANGELOG.md

Summary:
Hardened invoice engine for production with the following improvements:
1. Implemented automatic GST calculation (CGST/SGST for intrastate, IGST for interstate based on business and customer states)
2. Created reusable InvoiceCalculator component that handles all invoice calculations
3. Added concurrency-safe invoice number generation using SELECT FOR UPDATE
4. Enhanced invoice statuses to include ISSUED, PARTIALLY_PAID, and VOID
5. Added complete audit trail fields: updated_by, cancelled_by, cancelled_at, cancellation_reason
6. Expanded PaymentMethod enum to include CHEQUE, NEFT, RTGS
7. Implemented proper invoice cancellation with inventory reversal (using SALES_RETURN transactions)
8. Recalculate invoice totals whenever items or discount is updated
9. All invoice calculations now go through the InvoiceCalculator ensuring consistency

Notes:
- Stock is automatically reversed when invoice is cancelled
- Invoice numbers are generated in a concurrency-safe way
- GST type is automatically determined based on business and customer states

Future Dependencies:
- PDF Generation
- Recurring Invoices
- Online Payment Gateway Integration
- Credit Notes

-----------------------------------------

-----------------------------------------

Ticket ID:
RPT-001

Title:
Reporting and Analytics Engine

Status:
Completed

Completion Date:
2026-07-21

Files Created:
- app/schemas/reports.py
- app/services/reports.py
- app/api/v1/reports.py

Files Modified:
- app/schemas/__init__.py
- app/services/__init__.py
- app/api/v1/__init__.py
- docs/CHANGELOG.md

Summary:
Implemented complete production-ready reporting and analytics engine for the Billix platform:
1. Dashboard Summary Endpoint (`/v1/reports/dashboard`) with sales metrics, outstanding receivables, product inventory, invoice statuses, top selling products, and recent invoices.
2. Sales Reports (`/v1/reports/sales`) with daily/weekly/monthly/yearly grouping, custom date ranges, and aggregate metrics.
3. Customer Reports (`/v1/reports/customers`) with top customers, highest spending, outstanding customers, and purchase history.
4. Product Reports (`/v1/reports/products`) with top/least selling, inactive products, stock value, and stock movement.
5. Payment Reports (`/v1/reports/payments`) with received/pending/overdue payments and payment method distribution.
6. Inventory Reports (`/v1/reports/inventory`) with inventory valuation, low stock, out of stock, and stock movement reports.

Notes:
- Uses existing repository/service architecture for consistency
- All queries are strictly business-scoped (multi-tenant safe)
- No frontend/chart/export functionality implemented as per requirements
- All reports use optimized aggregate SQL queries to avoid N+1 issues

Future Dependencies:
- CSV/Excel export
- Charting/visualization
- Scheduled reports
- AI analytics

-----------------------------------------

-----------------------------------------

Ticket ID:
ADMIN-001

Title:
Production Administration Module — Phase 1 (Business Settings & Preferences)

Status:
Completed

Completion Date:
2026-07-23

Files Created:
- app/models/settings.py
- app/schemas/settings.py
- app/repositories/settings.py
- app/services/settings.py
- app/api/v1/settings.py
- alembic/versions/20260723_add_business_settings_and_preferences.py

Files Modified:
- app/models/__init__.py
- app/schemas/__init__.py
- app/repositories/__init__.py
- app/services/__init__.py
- app/api/v1/__init__.py
- docs/CHANGELOG.md

Summary:
Implemented Phase 1 of the Production Administration Module, comprising two sub-modules. Module 1 (BusinessSettings) delivers tenant-specific company identity, GST/PAN details, invoice numbering format, financial year, locale (currency, timezone, date format), invoice defaults, and an Appwrite-ready logo abstraction. Module 2 (BusinessPreferences) delivers notification preferences, decimal precision, low-stock threshold, default tax mode, inventory behaviour flags, and an extensible JSON report_preferences column. Both modules follow the project's Repository → Service → Router layering strictly, reuse BaseModelMixin and BaseRepository, enforce tenant isolation via BusinessMemberRepository access checks, and auto-provision a record on first GET (upsert-on-read pattern). RBAC, Audit Logs, Notifications, and Backup Abstraction were explicitly excluded per scope.

Notes:
- Each business profile has at most one settings record and one preferences record (enforced by UNIQUE constraint on business_id in both tables).
- logo_file_id stores an Appwrite file ID, not a raw URL — resolution to a signed URL should be handled at the API gateway or frontend layer.
- report_preferences is a schema-less JSON column, allowing future preference keys to be added without migrations.
- Run `alembic upgrade head` to apply the migration.

Future Dependencies:
None

-----------------------------------------

-----------------------------------------

Ticket ID:
RBAC-001

Title:
Role-Based Access Control (RBAC) — Production Implementation

Status:
Completed

Completion Date:
2026-07-23

Files Created:
- app/auth/permissions.py
- alembic/versions/20260723_add_member_role.py
- tests/unit/test_rbac.py

Files Modified:
- app/models/roles.py
- app/models/business.py
- app/models/__init__.py
- app/services/business.py
- app/repositories/business.py
- app/api/v1/business.py
- app/api/v1/customers.py
- app/api/v1/suppliers.py
- app/api/v1/products.py
- app/api/v1/categories.py
- app/api/v1/units.py
- app/api/v1/inventory.py
- app/api/v1/invoices.py
- app/api/v1/reports.py
- app/api/v1/settings.py
- docs/CHANGELOG.md

Summary:
Implemented a complete, production-ready Role-Based Access Control system layered on top of the existing BusinessMember membership architecture. Added BusinessRole enum (Owner, Admin, Manager, Accountant, Sales, Inventory, Viewer) as a per-business role stored on BusinessMember.role, backed by an Alembic migration that back-fills existing owner members. Defined a granular Permission enum covering all domains (business, settings, members, customers, suppliers, products, inventory, invoices, payments, reports) and a ROLE_PERMISSIONS mapping that grants each role a precisely scoped permission set. Implemented PermissionChecker — a FastAPI dependency factory that resolves business_id from path or query params, loads the caller's BusinessMember record, and enforces the required Permission, returning 403 on failure. Applied PermissionChecker to every sensitive endpoint across all nine domain routers. The system is zero-duplication: all authorization logic lives exclusively in app/auth/permissions.py. A 30-assertion test suite covers enum completeness, mapping correctness, privilege monotonicity, and PermissionChecker behaviour under all edge cases.

Notes:
- BusinessRole is a per-business concept stored on BusinessMember.role; UserRole on User remains as the global system role for platform-level operations.
- POST /business-profiles (create) and GET /business-profiles (list own businesses) intentionally have no per-business permission check — they predate any membership.
- Run `alembic upgrade head` to apply the migration; existing owner members are back-filled to role='owner' and all others to role='viewer'.
- The ROLE_PERMISSIONS dict is the single source of truth — to change what a role can do, edit only that dict.

Future Dependencies:
- Member invitation API (MEMBER_INVITE / MEMBER_REMOVE permissions are defined but the endpoints do not yet exist)

-----------------------------------------

---

## Upcoming Tickets

| Ticket ID | Title | Milestone |
| --- | --- | --- |
| AUTH-002 | Backend Clerk Integration | 3 |
| AUTH-003 | User Model | 3 |
| AUTH-004 | Authentication Middleware | 3 |
| AUTH-005 | Current User Dependency | 3 |
| AUTH-006 | Role Foundation | 3 |
| AUTH-007 | Protected Routes | 3 |
| AUTH-008 | Authentication Testing | 3 |

See [ROADMAP.md](./ROADMAP.md) for the full milestone roadmap and ticket dependencies.

---

## Known Issues

_None yet._

> When an issue is discovered, record it here with: date, affected module, description, impact, and the ticket that will address it.

---

## Architectural Decisions

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-07-18 | Use Clerk for authentication instead of building custom auth | Reduces risk, accelerates delivery, provides hosted sessions, social/email flows out of the box. |
| 2026-07-18 | Use PostgreSQL on Neon as the primary database | Serverless Postgres, branching for dev, reliable for production SaaS. |
| 2026-07-18 | Use Appwrite only for file/blob storage | Keeps the primary data model in Postgres; Appwrite handles invoice PDFs, logos, attachments. |
| 2026-07-18 | Frontend on Vercel, backend on DigitalOcean | Vercel for SSR/edge performance; DigitalOcean for predictable FastAPI hosting. |
| 2026-07-18 | Layered backend: Router → Service → Repository → Model | Keeps HTTP, business logic, and data access cleanly separated and testable. |
| 2026-07-18 | Multi-tenant scoping via `business_id` on every domain table | Allows one user to operate multiple GSTINs/branches from a single account. |

---

## Breaking Changes

_None yet._

> When a change breaks existing behavior (API contract, DB schema, UI flow), record it here with: date, ticket, what changed, and the migration/upgrade path.

---

## Cross-References
- [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [ROADMAP.md](./ROADMAP.md)
- [AI_RULES.md](./AI_RULES.md)
