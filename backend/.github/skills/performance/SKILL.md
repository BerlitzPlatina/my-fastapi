---
name: performance
description: 'Performance review workflow for this backend. Use when checking slow routes, expensive MongoDB queries, async I/O bottlenecks, validation overhead, repeated work, or resource usage risks.'
argument-hint: 'Describe the slow code path, route, query, or performance concern'
---

# Performance

Use this skill when the goal is to review code for performance risk rather than to rewrite functionality. Focus on where latency, wasted work, or resource pressure is likely to come from in this backend.

## What This Skill Produces

- A focused performance review of the slow path or risky code.
- A short list of likely bottlenecks ranked by impact.
- Practical suggestions that preserve correctness and fit the repository's patterns.
- A quick validation idea for the suspected hotspot.

## When to Use

- A route feels slow or expensive.
- A MongoDB query may be doing too much work.
- Async I/O may be blocking or repeated unnecessarily.
- Validation, serialization, or model conversion seems costly.
- A change may increase memory, CPU, or request latency.
- You need to review a patch for performance regressions.

## Quick Checklist

1. Identify the slow path or suspected hotspot.
2. Read the nearest code that controls the cost.
3. Look for repeated queries, repeated model work, or unnecessary conversions.
4. Check whether indexes, filters, or pagination are doing enough work reduction.
5. Verify async calls are truly awaited and not accidentally serialized.
6. Prefer the smallest change that reduces cost without changing behavior.
7. Note one focused way to validate the improvement.

## Decision Points

### Query vs Application Overhead

- Treat it as a query problem when the database is doing too much scanning, sorting, or fetching.
- Treat it as application overhead when the route repeats validation, conversion, or helper work.
- If both contribute, start with the layer that is easiest to measure and cheapest to change.

### Optimize vs Defer

- Optimize now if the slow path is on the critical request path or is obviously wasteful.
- Defer optimization if the concern is speculative and there is no clear hot path.
- Prefer one focused improvement over multiple low-confidence tweaks.

### Behavior vs Cost

- Preserve response shape and correctness unless the request explicitly allows a change.
- If a performance fix changes behavior, call that out explicitly.

## Repository Cues

- This backend uses FastAPI routes, `DatabaseDep`, CRUD helpers, and async Motor/MongoDB access.
- Mongo query cost often depends on filters, projections, sorting, and indexes.
- `_id`/`id` mapping and Pydantic validation can add overhead if repeated unnecessarily.
- Useful repo validation commands are `bash ./scripts/lint.sh` and `bash ./scripts/test.sh`.

## Quality Checks

- The suspected bottleneck is local and plausible.
- The recommendation targets the controlling layer, not just a nearby caller.
- The suggestion preserves correctness or clearly states any tradeoff.
- The review distinguishes actual hotspots from premature optimization.
- A follow-up check is suggested for the changed slice.

## Output Expectations

When responding, include:

1. The suspected hotspot.
2. Why it is likely expensive.
3. The most effective change.
4. Any tradeoff or correctness risk.
5. A simple validation path.

## Example Prompts

- `/performance Review this route for slow query patterns`
- `/performance Find the biggest bottleneck in this FastAPI handler`
- `/performance Check whether this MongoDB access is doing unnecessary work`
- `/performance Review this patch for performance regressions`