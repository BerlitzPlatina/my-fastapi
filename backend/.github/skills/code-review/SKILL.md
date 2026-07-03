---
name: code-review
description: 'Structured code review workflow. Use when reviewing diffs, pull requests, or local changes for bugs, regressions, risky behavior, FastAPI misuse, missing tests, and validation gaps.'
argument-hint: 'Describe the change, diff, file, or review target'
---

# Code Review

Use this skill to review code changes with a findings-first mindset. The goal is to identify real defects, behavioral regressions, risky assumptions, and missing validation before summarizing what changed.

## What This Skill Produces

- A review ordered by severity, with the highest-risk findings first.
- Concrete bug, regression, and test-gap findings tied to specific files.
- A brief statement of assumptions, open questions, residual risk, and only then a short summary.

## When to Use

- Review a pull request, diff, staged change, or edited file.
- Check whether a bug fix actually covers edge cases.
- Inspect FastAPI route, dependency, auth, CRUD, or Pydantic changes for regressions.
- Evaluate whether tests and validation are sufficient for the touched behavior.

## Review Priorities

1. Correctness bugs.
2. Behavioral regressions.
3. Broken contracts between routes, schemas, dependencies, and persistence.
4. Missing or weak tests for the changed behavior.
5. Risky assumptions, error handling gaps, typing issues, and maintainability concerns that are likely to cause defects.

## Procedure

1. Anchor the review to the changed surface.
   Start from the concrete files, diff, symbols, or failing behavior named in the request.

2. Read the deciding code path, not the whole repo.
   Prefer the changed function, its immediate call sites, the owning route or dependency, and the nearest test over broad exploration.

3. Reconstruct intended behavior.
   Identify what the code is supposed to do now, what it did before when that matters, and what inputs or states are security-sensitive or failure-prone.

4. Pressure-test the change.
   Look for mismatches between:
   - request models and returned payloads
   - dependency annotations and FastAPI injection behavior
   - async database operations and expected control flow
   - auth checks and privilege boundaries
   - changed logic and test coverage

5. Validate with the cheapest focused check when available.
   Prefer a narrow test, then repo lint/type checks, then broader test coverage if the changed behavior spans multiple layers.

6. Report findings first.
   Lead with defects and risks, ordered by severity. Do not start with a broad summary.

7. Add assumptions and residual risk.
   If a concern depends on missing context, state that explicitly.

8. Summarize briefly.
   Only after findings, questions, and risks, add a short change summary or note that no findings were discovered.

## Decision Points

### Whether Something Is a Finding

- Report it as a finding if it can plausibly break runtime behavior, API contracts, auth, validation, persistence, or test reliability.
- Do not elevate style-only preferences unless they create a real defect risk.
- If you cannot confirm the impact, phrase it as a risk or open question, not a definite bug.

### No Findings Case

- State explicitly that no findings were discovered.
- Mention residual risk, such as missing executable validation or uncovered edge cases.

### Validation Depth

- If one file changed and a focused test exists, use that.
- If signatures, typing, or imports changed, include lint/type validation.
- If request flow, auth, or persistence changed, prefer targeted tests and broaden only if needed.

## Repository Cues

- FastAPI dependency annotations matter: route database parameters should use `DatabaseDep` from `app/api/deps.py` rather than a plain fallback type.
- This backend uses async Motor/MongoDB patterns, so review awaited operations and document-to-model conversion carefully.
- Pydantic schema conversions should be checked for runtime validation behavior, especially across similar but distinct request models.
- Useful validation commands in this repo are `bash ./scripts/lint.sh` and `bash ./scripts/test.sh`.

## Output Format

Use this structure when responding:

1. Findings.
   Each finding should include severity, why it matters, and the affected file or symbol.

2. Open questions or assumptions.
   Include only when they materially affect confidence.

3. Brief summary.
   Keep this secondary to findings.

If there are no findings, say so directly before noting residual risks or testing gaps.

## Quality Checks

- Findings are specific, testable, and tied to behavior.
- Severity ordering is defensible.
- The review distinguishes definite bugs from lower-confidence risks.
- Missing tests are called out when behavior changed without adequate coverage.
- Summary content does not bury the most important defect.

## Example Prompts

- `/code-review Review these FastAPI auth changes for regressions`
- `/code-review Review the diff in users routes and tell me what will break`
- `/code-review Check whether this bug fix has missing tests`
- `/code-review Review local backend changes with a findings-first report`