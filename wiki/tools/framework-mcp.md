---
verified_at: 2026-08-10
status: removed
scope: stack:erp-supabase
---

# framework-mcp

**removed** as of 2026-08-10, for **stack:erp-supabase**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-10 | stack:erp-supabase | **removed** | 0 calls in 2,396 sessions; declared for two project paths that left `repos.txt` today | Project-scoped MCP server for a terminated project — vendor name withheld, it is in `.leakpatterns`. A server for a stack that no longer exists cannot become useful later, so no trial is owed. Config edit is the user's — `~/.claude.json` still declares it, and the next `reconcile.py` will disagree with this row until it does not. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
