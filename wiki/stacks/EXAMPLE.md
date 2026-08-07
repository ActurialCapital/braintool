---
verified_at: YYYY-MM-DD
repo: ~/path/to/repo
---

# Stack: <name>

The fit test for any candidate tool: does it help **this**?

Real stack pages live only on the workstation — `wiki/stacks/*` is gitignored,
because a stack profile is a map of a private codebase. This file is the template.

## What it actually is

Framework, language, database, hosting. Be specific about what it is **not** —
"deploys to Cloud Run, not Vercel" is the line that rejects a whole category of
otherwise-appealing tools.

## Churn baseline

`python3 bin/churn.py <repo>` → **fix:feat**, overall and per scope.

| Scope | feat | fix | ratio |
|---|---:|---:|---:|
| example | 9 | 45 | **5.00** |

A scope far above the repo average is a question, not a verdict: is the tooling
for that area unused, or unhelpful? Both answers are worth having.

## Tools that connect to this stack

List the MCP servers, skills, and plugins that actually touch this codebase, with
their invocation counts from `bin/reconcile.py`. A tool listed here with zero
invocations is the highest-value finding in the file.

## Fit filter

The standing noes. Anything matching these is rejected without a security scan,
because fit fails first and costs nothing to check.
