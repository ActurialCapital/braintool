---
verified_at: 2026-08-10
status: recorded
scope: global
---

# claude-mem

**recorded** as of 2026-08-10, for **global**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-10 | global | **recorded** | 951 of 2,396 sessions covered (~40%); 8,126 prompts, 6,444 summaries, 32,114 observations in a plain SQLite file | Read as **optional enrichment, never the store of record.** Coverage is the disqualifier: a 60% hole would hide findings without saying so. Trust splits three ways — `user_prompts` is verbatim and better than any regex, `session_summaries` point at sessions worth opening, `observations` are another model's judgement and are not evidence. The dependency stays soft: stdlib `sqlite3` reads the file whether or not the plugin runs, so this row never blocks removing it. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
