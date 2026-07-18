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
