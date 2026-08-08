---
verified_at: 2026-08-08
status: rescoped
scope: stack:next-vercel
---

# vercel-skills

**rescoped** as of 2026-08-08, for **stack:next-vercel**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-08 | stack:next-vercel | **flagged** | 6 skills, **0 invocations** each, global | `deploy-to-vercel`, `vercel-cli-with-tokens`, `vercel-composition-patterns`, `vercel-optimize`, `vercel-react-best-practices`, `vercel-react-native-skills`, `vercel-react-view-transitions`. The 2026-08-07 rescope moved the *plugin* to project scope and left the *skills* global — a half-done fix reported as done. They load in every unrelated session. |
| 2026-08-08 | stack:next-vercel | **rescoped** | 7 skills moved out of global into 2 repos | Now load only where a Vercel deploy exists. Completes the 2026-08-07 rescope, which moved the plugin and left the skills behind. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
