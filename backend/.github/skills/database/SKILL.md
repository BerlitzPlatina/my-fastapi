---
name: database
description: 'Database workflow for this backend. Use when changing MongoDB access, Motor queries, indexes, document-to-model mapping, persistence bugs, or database-related FastAPI behavior.'
argument-hint: 'Describe the collection, query, mapping, bug, or database change'
---

# Database

Use this skill for backend database work in this repository. It is designed for the actual stack here: MongoDB with Motor, explicit document-to-model mapping, and FastAPI dependency-based access to the database.

## What This Skill Produces

- A repo-aligned database change, bug fix, or review.
- Focused reasoning about collections, queries, indexes, and model mapping.
- Validation that the changed persistence behavior still matches route and schema expectations.

## When to Use

- Add or change a MongoDB query.
- Fix database-related bugs in CRUD or route handlers.
- Update document-to-model conversion logic.
- Add or review indexes.
- Trace persistence issues between FastAPI routes, CRUD helpers, and Mongo documents.
- Check whether a database change preserves response-model behavior.

## Repository Cues

- The backend uses async Motor via `app/core/db.py`.
- Database access should flow through `DatabaseDep` and `get_database()`.
- Collections are accessed directly, for example `db.users` and `db.items`.
- Mongo documents use `_id`, while Pydantic models expose `id`; mapping is handled explicitly in CRUD helpers.
- Startup index creation lives in `ensure_indexes()` inside `app/core/db.py`.
- Useful broad validation commands in this repo are `bash ./scripts/lint.sh` and `bash ./scripts/test.sh`.

## Procedure

1. Start from the controlling persistence path.
   Identify the concrete route, CRUD helper, model conversion, or startup database function involved.

2. Read only the nearest deciding code.
   Prefer the route that issues the operation, the CRUD function that performs it, the model used for validation, and any nearby test.

3. Form one falsifiable local hypothesis.
   State what should be stored, queried, updated, or returned, and name one cheap check that could prove that assumption wrong.

4. Check the document-model boundary.
   Verify how `_id`, UUIDs, timestamps, owner fields, hashed secrets, and optional fields move between Mongo documents and Pydantic models.

5. Make the smallest grounded change.
   Fix the query, mapping, update payload, index, or dependency usage at the narrowest layer that actually controls behavior.

6. Validate immediately after the first substantive edit.
   Prefer, in order:
   - a focused test for the changed CRUD or route behavior
   - a narrow lint or type check if signatures or imports changed
   - broader backend tests only when the behavior crosses multiple layers

7. Iterate locally if validation fails.
   Repair the same slice first and rerun the same focused check before widening scope.

8. Close with the persistence effect.
   Summarize what changed in storage or query behavior, what stayed compatible, and what validation confirmed it.

## Decision Points

### Route vs CRUD vs DB Core

- Start in `app/api/routes/` if the issue appears in request handling, dependency injection, status codes, or response shapes.
- Start in `app/crud.py` if the issue is query logic, update payloads, lookup behavior, or document conversion.
- Start in `app/core/db.py` if the issue is connection lifecycle, index creation, or database initialization.

### Query vs Mapping Bug

- Treat it as a query bug when the wrong documents are selected, updated, ordered, or deleted.
- Treat it as a mapping bug when Mongo data is correct but the Pydantic model, `_id` conversion, UUID handling, or response payload is wrong.

### Index Changes

- Add or modify an index only when a real lookup, uniqueness, or ordering need exists.
- Keep index creation centralized in startup code unless the repository establishes a different pattern.

## Quality Checks

- Async database operations are awaited correctly.
- `_id` and `id` conversions remain deliberate and consistent.
- Query filters and update payloads match the intended types and field names.
- Route response models still match the data returned after persistence changes.
- Index changes match real query behavior or uniqueness requirements.
- Validation covers the touched behavior as narrowly as possible.

## Output Expectations

When responding, include:

1. Which layer controlled the behavior: route, CRUD, or db core.
2. What persistence or mapping issue was fixed or reviewed.
3. What validation was run.
4. Any remaining risk, such as uncovered edge cases or untested index behavior.

## Example Prompts

- `/database Fix this Mongo query returning the wrong user`
- `/database Review this CRUD change for document-to-model mapping bugs`
- `/database Add the right index for this lookup path`
- `/database Debug why this FastAPI route returns the wrong data after saving`