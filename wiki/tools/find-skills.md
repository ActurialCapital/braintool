---
verified_at: 2026-08-10
status: removed
scope: global
---

# find-skills

**removed** as of 2026-08-10, for **global**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-10 | global | **removed** | 0 invocations since 2026-03-17; `tool-decisions` declares the same trigger phrase | **Superseded, not unused.** It answers "what could I install" — which `discover.sh` already does — while `tool-decisions` claims `"is there a skill for X"` in its own description and checks the ledger first. Two skills competing for one phrasing; the more specific one wins. Recorded as supersession so the next reader sees why it lost rather than assuming it was bad. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
