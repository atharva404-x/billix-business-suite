# Billix — AI Rules

> **MANDATORY** rulebook for every AI assistant (Bolt AI, Cursor, Claude, ChatGPT, Jules, Trae, etc.) working on Billix.
> Read this file in full BEFORE writing any code or proposing any change.
> Violating any rule below is grounds for reverting the change.

---

## 0. Standard Prompt — Read Before Starting Work

> Every AI assistant MUST run through this prompt silently (or out loud) before producing any output for Billix.

```
You are working on Billix, a production-ready GST Billing, Inventory &
Business Management SaaS for Indian businesses.

Before doing anything, you MUST:
1. Read docs/PROJECT_CONTEXT.md — understand what Billix is and its current status.
2. Read docs/ARCHITECTURE.md — understand structure, patterns, and protected files.
3. Read docs/ROADMAP.md — confirm the current milestone and the ONE ticket in scope.
4. Read docs/CHANGELOG.md — check prior work on the same area.
5. Read docs/AI_RULES.md — internalize the rules below.

Then:
- Confirm the single engineering ticket you are assigned.
- Scope your work to that ticket ONLY.
- Reuse existing components/services before creating new ones.
- Ask for clarification on any ambiguity instead of assuming.
- Explain every file modification you make.
- Update docs/CHANGELOG.md when the ticket is complete.
- Stop. Do not start the next ticket without explicit approval.

You are building production software, not a demo. No throwaway code.
```

---

## 1. Scope & Conduct

1. **Complete only one engineering ticket at a time.** Never combine tickets.
2. **Never implement future milestones.** Only the current milestone's tickets are in scope.
3. **Never redesign the architecture.** If you believe a structural change is needed, propose it and wait for approval.
4. **Never modify unrelated files.** Touch only the files required by your assigned ticket.
5. **Stop after completing the assigned ticket.** Do not "helpfully" start the next one.
6. **Ask for clarification instead of making assumptions.** Ambiguity → question, not invention.
7. **Explain every file modification.** List created/modified files and the reason for each change.

## 2. Code Quality

8. **Never create demo code.** No placeholder logic, no `TODO`s, no hardcoded fake data in production paths.
9. **Always reuse existing code where possible.** Search `components/common`, `lib/utils`, backend services/repositories before adding new code.
10. **Follow SOLID principles.** One responsibility per module/class; depend on abstractions at boundaries.
11. **Follow the existing folder structure.** Do not invent parallel hierarchies.
12. **Keep modules loosely coupled.** Domain modules talk via services, not by importing each other's internals.
13. **Use production-ready coding practices.** Validation at boundaries, typed inputs/outputs, error states surfaced to the user.
14. **No dead code.** Delete what you replace — no `_old` files, no commented-out blocks.
15. **No premature abstraction.** Introduce a shared helper only with ≥2 concrete call sites and a clear shared shape.
16. **Comments:** default to none. Add a comment only when the *why* is non-obvious.
17. **Never leave `console.log`, `print`, or debug statements in committed code.**

## 3. Data & Security

18. **User data is sacred.** No destructive operations (DROP, hard DELETE) without explicit confirmation and reversibility.
19. **Never edit a shipped Alembic migration.** Always add a new migration.
20. **Never hardcode secrets.** All secrets live in environment variables.
21. **Every backend route is authenticated** unless explicitly designated public.
22. **Every input is validated** at the boundary (Pydantic on BE, zod on FE where applicable).
23. **RLS / tenant scoping is mandatory** on every multi-tenant table.

## 4. Tooling & Conventions

24. **Never edit** `src/routeTree.gen.ts` — it is auto-generated.
25. **Never remove `<Outlet />`** from `src/routes/__root.tsx`.
26. **Never modify protected files** listed in [ARCHITECTURE.md §11](./ARCHITECTURE.md) without approval.
27. **Match the codebase's conventions** — naming, imports, error handling, formatting.
28. **One ticket per commit/PR.** Reference the ticket ID in the commit message.
29. **Run lint + type checks + tests** before declaring a ticket complete.

## 5. Documentation & Changelog

30. **Update `docs/CHANGELOG.md` after every completed ticket.** Append a new entry under "Completed Engineering Tickets" using the standard format.
31. **Never rewrite past CHANGELOG entries.** The changelog is append-only.
32. **Reference related docs** (ARCHITECTURE, ROADMAP) in your CHANGELOG entry where relevant.

## 6. Frontend-Specific Rules

33. **Use TanStack Router file-based routing.** Do not create `src/pages/`, `_app/`, or `app/layout.tsx`.
34. **Use design tokens from `src/styles.css`.** No hardcoded color literals in components.
35. **Use shadcn/ui primitives** from `components/ui` before introducing new UI libraries.
36. **Use TanStack React Query** for server state. Do not replicate server state in component state.
37. **Mock data in `src/lib/mock-data.ts` is for scaffolding only.** Production paths must use real API + Query.
38. **Verify UI changes in the dev server** before reporting a ticket complete. If you cannot, say so explicitly.

## 7. Backend-Specific Rules

39. **Layer strictly:** Router → Service → Repository → Model. No skipping layers.
40. **Routers hold no business logic.** Services hold no HTTP awareness.
41. **Pydantic schemas never leak ORM models.** Map explicitly.
42. **Every write goes through Alembic.** Never `Base.metadata.create_all` in production.
43. **Async-first.** `async def`, async SQLAlchemy sessions.
44. **Type hints required** on every function.

## 8. Communication

45. **Report outcomes faithfully.** Never claim "all tests pass" or "deployed successfully" when they did not.
46. **Surface blockers immediately.** Do not silently work around a failing check.
47. **Summarize in plain language** what was accomplished, and suggest logical next steps.
48. **Length:** keep user-facing text concise. Match the task — a simple question gets a direct answer.

---

## 9. Forbidden Actions (require explicit approval)

- Modifying any file in [ARCHITECTURE.md §11 "Files & Folders That Must Never Be Modified Without Approval"](./ARCHITECTURE.md).
- Changing the tech stack (React, TanStack, FastAPI, Postgres, Clerk, Appwrite, Sentry).
- Adding new top-level dependencies (npm packages, Python packages) without confirmation.
- Dropping or renaming database tables/columns.
- Force-pushing, rewriting published git history, or squashing already-published commits.
- Deleting user data or running destructive migrations.
- Changing deployment targets (Vercel / DigitalOcean) or CI/CD pipelines.

---

## 10. Required Reading Order

1. [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md)
2. [ARCHITECTURE.md](./ARCHITECTURE.md)
3. [ROADMAP.md](./ROADMAP.md)
4. [CHANGELOG.md](./CHANGELOG.md)
5. This file (`AI_RULES.md`)

If any of these documents contradict each other, raise the contradiction to the user instead of picking a side.
