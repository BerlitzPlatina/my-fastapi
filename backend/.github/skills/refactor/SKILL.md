---
name: refactor
description: 'Structured refactoring workflow. Use when improving code structure, readability, naming, duplication, or boundaries without intentionally changing behavior, while validating each step with focused checks.'
argument-hint: 'Describe the code to refactor, the smell, or the target improvement'
---

# Refactor

Use this skill when code needs to be reorganized, simplified, renamed, or decomposed without changing intended behavior. The goal is to make the code easier to understand and maintain while keeping risk controlled through small edits and immediate validation.

## What This Skill Produces

- A behavior-preserving refactor with minimal scope.
- A clear path from the current code smell to the smallest safe change.
- Focused validation after each substantive edit.
- A brief summary of what improved and what was used to confirm behavior stayed intact.

## When to Use

- Reduce duplication.
- Improve names, boundaries, or function extraction.
- Simplify control flow or data flow.
- Isolate responsibilities in routes, helpers, services, or models.
- Prepare code for a follow-up feature or bug fix.
- Clean up code that is correct but unnecessarily hard to read or maintain.

## What Not to Do

- Do not mix broad behavior changes into the refactor unless the request explicitly asks for them.
- Do not fix unrelated issues just because they are nearby.
- Do not rewrite large surfaces when a smaller local change will solve the actual problem.
- Do not skip validation after the first substantive edit when a focused check exists.

## Procedure

1. Find the controlling slice.
   Start from the specific file, symbol, test, or smell named in the request.

2. Read only the nearest deciding code.
   Prefer the owning function, class, route, helper, or neighboring test over broad exploration.

3. State one local refactoring hypothesis.
   Identify what structural problem exists, what should become simpler, and what cheap check can disconfirm that behavior changed.

4. Choose the smallest behavior-preserving edit.
   Examples: rename one symbol precisely, extract one helper, collapse one branch, or move one responsibility boundary.

5. Make the first substantive edit.
   Keep the public contract stable unless the request explicitly includes an API change.

6. Validate immediately.
   Prefer, in order:
   - the narrowest existing test for the touched behavior
   - a focused compile, lint, or type check for the touched slice
   - a broader project test only if no narrower check exists

7. Iterate locally.
   If validation fails because of the refactor, repair the same slice and rerun the same focused check before widening scope.

8. Stop when the code smell is resolved.
   Do not continue polishing once the target improvement is achieved and validated.

## Decision Points

### Extraction vs Rename vs Reorganization

- Use renaming when the main problem is unclear intent.
- Extract a helper when one coherent subtask can be named and reused or read independently.
- Reorganize control flow when the behavior is correct but branching or nesting obscures it.
- Move code across modules only when the existing ownership boundary is the real source of confusion.

### Single Change vs Staged Refactor

- Use one edit when the transformation is obviously local and easy to validate.
- Use staged edits when the change affects multiple call sites, types, or boundaries.
- Between stages, run the cheapest focused validation available.

### Behavior Preservation

- If the refactor appears to require changed behavior, stop treating it as a pure refactor and state that explicitly.
- If a safer internal contract can be improved without affecting callers, prefer that route.

## Validation Strategy

- Choose checks that directly exercise the touched behavior.
- Reuse existing tests before inventing broad new coverage.
- If typing or imports changed, include a narrow lint or type check.
- If no executable validation exists, inspect the diff carefully and say that validation is limited.

## Repository Cues

- In this repo, useful broad validations are `bash ./scripts/lint.sh` and `bash ./scripts/test.sh`.
- FastAPI route dependency annotations matter, so preserve types like `DatabaseDep` during refactors.
- Async MongoDB/Motor paths should keep awaited behavior and document-to-model conversions intact.
- Pydantic schema construction and response-model boundaries should be treated as behavior-sensitive even during structural cleanup.

## Quality Checks

- The code is simpler in one specific way: naming, duplication, branching, dependency direction, or boundary clarity.
- The refactor is minimal relative to the requested improvement.
- Validation ran immediately after the first substantive edit when possible.
- No unrelated cleanup was bundled in.
- The final explanation distinguishes structural improvement from behavior change.

## Output Expectations

When responding, include:

1. What was structurally improved.
2. What behavior was intentionally preserved.
3. What validation was run.
4. Any remaining risk if validation was limited.

## Example Prompts

- `/refactor Simplify this FastAPI route without changing behavior`
- `/refactor Extract the duplicated user lookup logic into a helper`
- `/refactor Clean up this nested Python function and keep tests passing`
- `/refactor Improve naming and control flow in this backend module`