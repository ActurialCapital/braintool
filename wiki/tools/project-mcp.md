---
verified_at: 2026-08-07
status: fixed
scope: stack:erp-supabase
---

# project-mcp

**fixed** as of 2026-08-07, for **stack:erp-supabase**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-07 | stack:erp-supabase | **fixed** | 25 calls through 2026-08-05, then silence | Declared in `.mcp.json` but never approved, so 32 tools were silently dead. Approved. **Cost of the gap: unmeasured, but it is the project's own database tooling.** |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
