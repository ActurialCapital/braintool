---
verified_at: 2026-08-09
status: open
scope: global
---

# karpathy-guidelines

**open** as of 2026-08-09, for **global**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-09 | global | **open** | 4 sections; 3 already covered by an installed always-on rule set | Only §3 *Surgical Changes* is new — "every changed line traces to the request", don't improve adjacent code. §2 and §4 restate rules already loaded every turn. §1 ("if unclear, stop and ask") **contradicts** the standing rule to act on a sensible default rather than stall. Adopting the block would buy one idea, three duplicates and one conflict. Candidate action: lift §3 into global rules, install nothing. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
