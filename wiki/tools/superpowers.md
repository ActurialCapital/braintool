---
verified_at: 2026-08-10
status: open
scope: global
---

# superpowers

**open** as of 2026-08-10, for **global**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-07 | global | **removed** | 143 invocations, last 2026-08-06 | Actively used until removal — `brainstorming` 46, `writing-plans` 31, `subagent-driven-development` 29, `systematic-debugging` 19. Removed for context cost: a full 72-file repo clone at `~/.claude/commands/` dumping ~200 phantom slash commands into every session. **Capability gap open** — replacements (`adhd`, `design-first`, `diagnose`) have 0–1 uses. Backup: `superpowers-commands-backup.tgz`. |
| 2026-08-10 | global | **open** | removed 2026-08-07 — 3 days; 1,306 brainstorm / 613 plan / 1,280 debug-shaped sessions in 30 days | Proposal to restore 5 skills standalone was **withdrawn, not rejected**. Nobody misses a tool in three days, and the substitute already installed has never been tried. This is the removal-side blind window: after an install, zero invocations mean nothing for 14 days; after a removal, no pain means nothing either, and only the first has an automatic guard. Watch item. Re-evaluate 2026-08-21. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
