---
verified_at: 2026-08-08
status: flagged
scope: stack:erp-supabase
---

# db-test-skills

**flagged** as of 2026-08-08, for **stack:erp-supabase**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-08 | stack:erp-supabase | **flagged** | `database-migrations`, `e2e-testing`: 0 invocations | Plausibly right for the ERP stack — but that repo already has project-level `postgres-expert` and `playwright-e2e`, so these may be duplicates at the wrong scope. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
