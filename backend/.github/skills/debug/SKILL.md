---
name: debug
description: 'Structured debugging workflow. Use when investigating failing behavior, errors, regressions, unexpected runtime output, validation failures, or broken tests, with local hypotheses and focused validation.'
argument-hint: 'Describe the bug, error, failing behavior, or failing test'
---

# Debug

Use this skill when code is failing, behaving unexpectedly, or producing unclear runtime results. The goal is to identify the controlling code path quickly, form one falsifiable local hypothesis, test it with the cheapest discriminating check, and fix the root cause with minimal scope.

## What This Skill Produces

- A concrete debugging path from symptom to likely root cause.
- One local, falsifiable hypothesis at a time instead of broad speculation.
- A small grounded fix or a tightly scoped next diagnostic step.
- Focused validation showing whether the hypothesis was confirmed or falsified.

## When to Use

- A test is failing.
- A route, function, or script behaves incorrectly.
- FastAPI dependency injection, validation, auth, or response behavior is wrong.
- MongoDB persistence, query, or mapping behavior is inconsistent.
- A traceback, runtime exception, or type-related failure needs explanation and repair.
- A recent change introduced a regression and the controlling layer is unclear.

## What Not to Do

- Do not map the whole codebase before choosing a working hypothesis.
- Do not compare many possible causes when one nearby path can be checked cheaply.
- Do not keep editing without validating the current hypothesis.
- Do not fix unrelated defects that are not part of the current failing slice.

## Procedure

1. Start from the most concrete anchor.
   Use the failing test, traceback, route, command, file, or symbol named in the request.

2. Read only enough nearby code to identify the controlling path.
   Prefer the owning function, route, dependency, helper, or neighboring test over broad exploration.

3. Form one falsifiable local hypothesis.
   State what should be happening, why it is likely failing, and one cheap check that could disconfirm that idea.

4. Run the cheapest discriminating check.
   Prefer the narrowest failing test, targeted command, or nearest executable validation that can prove the hypothesis wrong.

5. Make the smallest grounded edit.
   Change the code that actually controls the behavior, not a nearby caller unless the caller is the real source.

6. Validate immediately after the first substantive edit.
   Prefer, in order:
   - the same focused failing check
   - a nearby behavior-scoped test
   - a narrow lint, type, or compile check
   - broader validation only if the bug crosses layers

7. Interpret the result before widening scope.
   - If the check passes, decide whether any adjacent follow-up is still needed.
   - If it fails in a way that supports the hypothesis, repair the same slice and rerun the same check.
   - If it falsifies the hypothesis, move one hop closer to the code that directly controls the behavior.

8. Close with explicit outcomes.
   Summarize the root cause, the fix, the validation run, and any remaining uncertainty.

## Decision Points

### Symptom vs Root Cause

- If the current code only forwards data, registers routes, or wires dependencies, step to the nearest code that computes, mutates, or decides behavior.
- If multiple nearby candidates exist, choose the path with the cheapest discriminating check.

### Validation Ambiguity

- If the first validation result is ambiguous, do one nearby read or one neighboring test check to disambiguate.
- Do not resume broad searching before making that local decision.

### Bug Fix vs Probe

- If confidence is low, the first edit may be a small reversible probe that exposes control-flow or validation gaps.
- If the bug is already localized, make the minimal direct fix first.

## Repository Cues

- In this repo, backend behavior often crosses FastAPI routes, `DatabaseDep`, CRUD helpers, and Pydantic models.
- Async Motor and MongoDB document mapping are common sources of persistence bugs.
- `_id` to `id` conversion boundaries should be checked whenever stored data and response data disagree.
- Useful broad validations in this repo are `bash ./scripts/lint.sh` and `bash ./scripts/test.sh`.

## Quality Checks

- The hypothesis was concrete enough to be falsified.
- The first validation was as narrow as the environment allowed.
- The fix touched the controlling slice instead of nearby incidental code.
- Scope stayed local until validation forced a wider move.
- The final explanation distinguishes symptom, root cause, and proof.

## Output Expectations

When responding, include:

1. The observed symptom.
2. The working hypothesis or confirmed root cause.
3. What check was used to validate it.
4. What changed and why it fixes the problem.
5. Any remaining risk if validation was limited.

## Example Prompts

- `/debug Figure out why this FastAPI route is returning 422`
- `/debug Debug this failing pytest case and fix the root cause`
- `/debug Trace this MongoDB mapping bug from route to CRUD`
- `/debug Explain this traceback and repair the broken behavior`