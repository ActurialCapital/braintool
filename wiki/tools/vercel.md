---
verified_at: 2026-08-07
status: rescoped
scope: stack:next-vercel
---

# vercel

**rescoped** as of 2026-08-07, for **stack:next-vercel**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-07 | stack:next-vercel | **rescoped** | 0 vercel.json / 0 package refs in <project> repos; <project> deploys to Cloud Run | Not removed — moved from user scope to the two projects that actually use it (see their stack pages). ~20 skills stopped loading in every unrelated session. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
