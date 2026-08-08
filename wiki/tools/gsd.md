---
verified_at: 2026-08-08
status: open
scope: global, stack:greenfield
---

# gsd

**open** as of 2026-08-08, for **stack:greenfield**.

> Different verdicts in different scopes. Both are true — read the row that matches the codebase in front of you.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-07 | global | **removed** | 0 invocations across 2,538 sessions; 0 spawns across all 33 agents | Pure dead weight. 33 agent descriptions loaded into every session's context for a framework nothing ever called. 3.4M on disk. |
| 2026-08-08 | stack:greenfield | **open** | 0 invocations in a mature codebase | The 2026-08-07 removal was recorded as global, which was wrong. gsd was never exercised **here** — a mature ERP with settled patterns. A greenfield project needing roadmap-and-phase planning is the case it was built for, and this ledger has no evidence either way. Not a rejection; an untested scope. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
