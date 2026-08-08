---
verified_at: 2026-08-07
status: removed
scope: global
---

# superpowers

**removed** as of 2026-08-07, for **global**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-07 | global | **removed** | 143 invocations, last 2026-08-06 | Actively used until removal — `brainstorming` 46, `writing-plans` 31, `subagent-driven-development` 29, `systematic-debugging` 19. Removed for context cost: a full 72-file repo clone at `~/.claude/commands/` dumping ~200 phantom slash commands into every session. **Capability gap open** — replacements (`adhd`, `design-first`, `diagnose`) have 0–1 uses. Backup: `superpowers-commands-backup.tgz`. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
