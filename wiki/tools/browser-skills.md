---
verified_at: 2026-08-08
status: rescoped
scope: stack:browser-automation, stack:react-app
---

# browser-skills

**rescoped** as of 2026-08-08, for **stack:react-app**.

> Different verdicts in different scopes. Both are true — read the row that matches the codebase in front of you.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-08 | stack:browser-automation | **flagged** | `autobrowse`, `browser-trace`: 0 invocations since 2026-05-03 | Stack-specific, global. Belong in a repo that does browser work, or nowhere. |
| 2026-08-08 | stack:react-app | **rescoped** | `autobrowse`, `browser-trace` → 4 React repos | Browser automation is only meaningful where there is a UI to drive. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
