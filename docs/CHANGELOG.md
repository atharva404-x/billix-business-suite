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
BUS-001

Title:
Business & Membership Data Model

Status:
Completed

Completion Date:
2026-07-18

Files Created:
- app/models/business.py
- app/models/membership.py
- tests/unit/test_tenant_models.py

Files Modified:
- app/models/user.py
- docs/CHANGELOG.md

Summary:
Designed and created the core business profile and membership database models establishing Billix's multi-tenant foundation. Set up SQL-level cascades, unique constraint indexes (gstin, pan), relationship back-population parameters, and explicit foreign key mapping configurations.

Notes:
- Explicitly defined 'foreign_keys="[Membership.user_id]"' on User relationships to prevent mapping conflicts when querying memberships with multiple User foreign key fields.
- Reusable BaseModelMixin was successfully applied across both models.

Future Dependencies:
TENANT-03
TENANT-04

-----------------------------------------

-----------------------------------------

Ticket ID:
BUS-002

Title:
Business Management

Status:
Completed

Completion Date:
2026-07-18

Files Created:
- app/schemas/__init__.py
- app/schemas/business.py
- app/repositories/__init__.py
- app/repositories/business.py
- app/services/__init__.py
- app/services/business.py
- app/api/__init__.py
- app/api/v1/__init__.py
- app/api/v1/businesses.py
- tests/unit/test_business_services.py

Files Modified:
- app/main.py
- docs/CHANGELOG.md

Summary:
Implemented the complete Business Service Layer and REST API endpoints supporting full CRUD operations on business profiles. Configured automatic creator membership linkage, duplicate GSTIN validation checks, and strict OWNER-only deactivation/updating policies.

Notes:
- Integrated a high-quality soft-deleted business filter inside list_by_user_id to exclude inactive businesses.
- Thoroughly tested direct BusinessService methods and REST endpoints via TestClient.

Future Dependencies:
TENANT-03
TENANT-04

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
