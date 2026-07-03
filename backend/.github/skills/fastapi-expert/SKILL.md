---
name: fastapi-expert
description: 'Expert workflow for FastAPI backend work in this repository. Use when implementing or debugging routes, dependencies, auth, Pydantic models, Motor/MongoDB access, validation errors, response models, or backend tests.'
argument-hint: 'Describe the backend change, bug, endpoint, or review target'
---

# FastAPI Expert

Use this skill for repeatable backend work in this repository: adding or changing endpoints, tracing request/response bugs, reviewing FastAPI changes, aligning models with MongoDB documents, and validating tests or typing.

## What This Skill Produces

- A repo-aligned implementation, bug fix, or review for FastAPI backend code.
- A narrow validation path using the project's real test and lint commands.
- Changes that follow the repository's dependency, typing, and database conventions.

## When to Use

- Add or modify routes under `app/api/routes/`.
- Change request or response models in `app/models.py`.
- Debug dependency injection, auth, token, or validation issues.
- Update CRUD or MongoDB query behavior in `app/crud.py` or `app/core/db.py`.
- Review backend changes for regressions, missing tests, or FastAPI misuse.

## Repository Cues

- The backend uses FastAPI with Motor/MongoDB, not SQLModel-backed request handling.
- Database dependencies should flow through `DatabaseDep` from `app/api/deps.py`.
- Mongo access is initialized in `app/core/db.py` and uses async collection operations.
- Backend validation commands are `bash ./scripts/test.sh` and `bash ./scripts/lint.sh`.
- Known repo gotchas:
  - Keep route database parameters typed as `DatabaseDep`; using plain `Any` can make FastAPI treat `db` as a request parameter.
  - When converting registration payloads to `UserCreate`, prefer explicit field construction over broad `model_validate(...)` on a different schema when runtime validation has already proven fragile.

## Procedure

1. Identify the controlling code path.
   Start from the concrete anchor named in the request: route, model, dependency, CRUD function, failing test, or error message.

2. Read only the nearest deciding code.
   Prefer the owning route, dependency, CRUD function, neighboring test, or schema definition over broad repo exploration.

3. Form one falsifiable local hypothesis.
   State what should happen or why it is failing, and name one cheap check that could disconfirm that hypothesis.

4. Make the smallest grounded edit.
   Fix the root cause when practical. Preserve existing API shapes and repository style unless the task requires a contract change.

5. Validate immediately after the first substantive edit.
   Prefer, in order:
   - the narrowest failing or behavior-scoped test
   - a focused route or CRUD test
   - `bash ./scripts/lint.sh` for typing and linting
   - `bash ./scripts/test.sh` when behavior needs broader confirmation

6. Iterate locally if validation fails.
   Repair the same slice first. Only widen scope if the failed check shows control lives one hop away.

7. Close with explicit outcomes.
   Summarize the behavioral change, the validation run, and any remaining risk or follow-up.

## Decision Points

### Route vs CRUD vs Dependency

- If the issue changes HTTP status codes, response payloads, request parsing, or dependency injection, start in `app/api/routes/` or `app/api/deps.py`.
- If the issue changes persistence, filtering, document mapping, or user lookup behavior, start in `app/crud.py` or `app/core/db.py`.
- If the issue is a validation mismatch, start in `app/models.py` and the route that constructs or returns that model.

### Review vs Implementation

- For implementation, edit the smallest slice that satisfies the requested behavior and then validate.
- For review, prioritize findings: bugs, regressions, contract mismatches, missing tests, and incorrect FastAPI dependency usage.

### Test Selection

- If a single route or helper is touched and a focused test exists, run that first.
- If typing, imports, or signatures changed, run `bash ./scripts/lint.sh`.
- If request flow or auth changed, run the relevant tests and then `bash ./scripts/test.sh` if needed.

## Quality Checks

- Dependency-injected parameters are typed consistently, especially `DatabaseDep` and current-user dependencies.
- Async Mongo calls are awaited and return values are mapped to response models intentionally.
- Response models and returned data shapes match.
- Error codes and error messages remain deliberate.
- New behavior is covered by a focused test when practical.
- Linting and typing still pass for the touched slice.

## Example Prompts

- `/fastapi-expert Fix why this users endpoint is treating db as a query parameter`
- `/fastapi-expert Review this auth route change for FastAPI regressions`
- `/fastapi-expert Add a new Mongo-backed endpoint and the minimal tests`
- `/fastapi-expert Debug a Pydantic response model validation error in users`