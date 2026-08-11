---
verified_at: 2026-08-11
status: adopted
scope: global
---

# rules-after-compact

**adopted** as of 2026-08-11, for **global**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-11 | global | **adopted** | rules last present `2026-08-10T15:21:08`; absent across a 734k→17k compaction while ~52KB of plugin hooks re-injected at `17:06:50`; 63 unsupervised minutes followed | A `/compact` writes a summary answering *"what are we doing"*. Goals survive it; **prohibitions do not**. At the boundary, caveman (902b), ponytail (8,567b), context-mode (16,531b) and claude-mem (23,946b) all re-announced themselves — because each owns a `SessionStart` hook. The *Surgical changes* rule appears exactly twice in 8.2MB, both at session start 26 hours earlier, and never again. What followed: five unrequested changes shipped to production in one 63-minute turn, four reverted, one issue reopened, ~2.5h lost. **Plugins survive compaction because they have a mechanism. Rules had none.** ~40 lines in `~/.claude/hooks/`, reading the sections straight out of `CLAUDE.md` so it cannot drift, silent on every non-compact start. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
