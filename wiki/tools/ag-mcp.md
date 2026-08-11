---
verified_at: 2026-08-11
status: open
scope: stack:erp-supabase
---

# ag-mcp

**open** as of 2026-08-11, for **stack:erp-supabase**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-11 | stack:erp-supabase | **open** | 11 calls, 5 sessions, last 2026-08-07 — not 0 | The standing open question asked whether it was "not being used, or not helping", on a zero that never existed. It *is* used, thinly. With `ag-grid` at 5.0 fix:feat and grid views recurring in the rework table, the question is now answerable and worth asking again — but 11 calls is too thin to judge either way. Re-ask after the counter has run a full week. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
