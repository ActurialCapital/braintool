---
verified_at: 2026-08-07
confidence: high
occurrences: 4
---

# Pattern: plugin removed, artifacts remain

Uninstalling a plugin disables it. It does **not** remove what it wrote into
`~/.claude/`. The leftovers keep loading into every session, invisibly, forever.

## Occurrences

| Tool | What stayed behind | Cost |
|---|---|---|
| [[superpowers]] | `~/.claude/commands/` was a full git clone of the repo — 72 md files, `.git`, `LICENSE`, `RELEASE-NOTES.md` | ~200 phantom slash commands per session, 3.5M |
| [[gsd]] | 33 agent files in `~/.claude/agents/`, 6 state files, `~/.claude/get-shit-done/` | 33 agent descriptions per session, 3.4M |
| [[sentrux]] | plugin cache, marketplace entry in `settings.json`, data dir | dormant, never enabled |
| failed installs | `temp_git_*` dirs in the plugin cache | 1.7M |

Total on one machine: **~17.7M and 230+ phantom entries**, none of it invokable.

## Why it is invisible

The cost is paid in context, per session, silently. Nothing errors. The only
symptom is a skill list that keeps growing and an agent that has read 200 command
descriptions before you typed anything.

## The mirror-image failure

The inverse also happens: *hooks left running after skills are deleted.* Recorded
as a learned rule on 2026-08-06 — "when removing a framework, grep `settings.json`
for its hooks". Both directions need checking.

## Detection

`bin/reconcile.py` flags any `~/.claude/{commands,agents}` content and reports
invocation counts. Zero invocations + not hook-activated + past grace period = orphan.

## The trap when cleaning up

Not everything named after the tool belongs to the tool. On 2026-08-07:

- `<repo>/docs/superpowers/` — **173 tracked files, cited from production source**
  (`<repo>/src/<file>.ts:254`). Kept. Only the directory *name* is stale.
- `<repo>/.planning/` — 317 tracked files, no references, untouched since
  2026-06-15. Genuinely stale.

Check `git ls-files` and grep for references before deleting anything inside a repo.
Config artifacts are disposable; work product wearing the tool's name is not.
