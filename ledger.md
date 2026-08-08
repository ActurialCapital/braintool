# Ledger

Every adopt / reject / remove decision, with the reason and the evidence.

**This file is the product.** Public catalogs already list what exists. Nothing
lists what *you* tried and dropped, and that record is the only thing that makes
the next decision better than the last one.

Rules:

- One row per decision. Never edit a past row — append a new one that supersedes it.
- **`scope` is a stack TYPE, not a repo name.** A tool can be right for one kind
  of codebase and wrong for another: `gsd` suits greenfield planning and not a
  mature ERP; `vercel` is essential to a Next deploy and dead weight elsewhere.
  A global "removed" erases that. Repo names stay out of this file — they are
  private, and the transferable question is about the *kind* of codebase.
  Same tool, different scope, different verdict = two rows, both true.
- `evidence` must be a number or a path, not an opinion.
- A removal is worth more than an adoption. Write the removals down first.

---

## 2026-08-07 — baseline audit

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-07 | [[superpowers]] | global | **removed** | 143 invocations, last 2026-08-06 | Actively used until removal — `brainstorming` 46, `writing-plans` 31, `subagent-driven-development` 29, `systematic-debugging` 19. Removed for context cost: a full 72-file repo clone at `~/.claude/commands/` dumping ~200 phantom slash commands into every session. **Capability gap open** — replacements (`adhd`, `design-first`, `diagnose`) have 0–1 uses. Backup: `superpowers-commands-backup.tgz`. |
| 2026-08-07 | [[gsd]] | global | **removed** | 0 invocations across 2,538 sessions; 0 spawns across all 33 agents | Pure dead weight. 33 agent descriptions loaded into every session's context for a framework nothing ever called. 3.4M on disk. |
| 2026-08-07 | [[sentrux]] | global | **removed** | 0 invocations | Installed in plugin cache + marketplace registered, never enabled, never used. |
| 2026-08-07 | [[gitingest-mcp]] | global | **removed** | Failed to connect: `ModuleNotFoundError: mcp.server.fastmcp` | Upstream package stale against current MCP SDK (FastMCP graduated out of `mcp`). Re-evaluate pinned, project-scoped, when this repo needs repo-ingest. |
| 2026-08-07 | [[vercel]] | stack:next-vercel | **rescoped** | 0 vercel.json / 0 package refs in <project> repos; <project> deploys to Cloud Run | Not removed — moved from user scope to the two projects that actually use it (see their stack pages). ~20 skills stopped loading in every unrelated session. |
| 2026-08-07 | [[project-mcp]] | stack:erp-supabase | **fixed** | 25 calls through 2026-08-05, then silence | Declared in `.mcp.json` but never approved, so 32 tools were silently dead. Approved. **Cost of the gap: unmeasured, but it is the project's own database tooling.** |
| 2026-08-07 | [[context-mode]] | global | **upgraded** | 1.0.107 → 1.0.169 | 62 versions behind; warned on every call. |
| 2026-08-07 | [[adhd]] | global | **adopted** | 0 uses (installed today) | Parallel divergent ideation. Partly fills the `superpowers:brainstorming` gap. Re-evaluate 2026-09-07. |
| 2026-08-07 | [[right-size]] | global | **adopted** | 0 uses (installed today) | Effort-matching gate, written in-house. Trigger-optimisation loop was run and **could not measure it** — its success looks identical to non-invocation. Judge on churn, not invocations. Re-evaluate 2026-09-07. |

## 2026-08-07 — first manual runs

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-07 | `setup-matt-pocock-skills` | global | **flagged** | installed 2026-05-02, **0 invocations**; upstream `mattpocock/skills` is candidate #3 (⭐208k) | A setup skill installed and never run, while its upstream sits in the sweep. Either adopt the source properly or drop the setup shim — holding both is the worst of each. |
| 2026-08-07 | fuzzy dedupe | global | **rejected** | 3 substring matches on `mattpocock/skills`, only 1 real | Considered auto-dropping candidates whose names resemble installed tools. Any repo ending in `-skills` matched `find-skills`. Cheap dedupe would hide real candidates; exact-match plus a human eye is correct here. |

## 2026-08-08 — Matt Pocock family review

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-08 | [[grill-me]] | global | **flagged** | installed 2026-05-02, **0 invocations** in 2,462 sessions | Installed via `~/.agents/skills/`. Real skill, plausible use (stress-test a plan), never once reached for. Keep or drop — but not "keep and never use". |
| 2026-08-08 | [[matt-pocock-skills]] | global | **flagged** | 13 skills installed, **1 invocation total** (`diagnose`) | `grill-me`, `grill-with-docs`, `improve-codebase-architecture`, `to-prd`, `to-issues`, `triage`, `tdd`, `autobrowse`, `browser-trace`, `find-skills`, `zoom-out`, `setup-matt-pocock-skills`. A whole family adopted at once on 2026-05-02, exercised once in three months. The largest block of unused surface in the harness. |

## 2026-08-08 — scope added

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-08 | [[gsd]] | stack:greenfield | **open** | 0 invocations in a mature codebase | The 2026-08-07 removal was recorded as global, which was wrong. gsd was never exercised **here** — a mature ERP with settled patterns. A greenfield project needing roadmap-and-phase planning is the case it was built for, and this ledger has no evidence either way. Not a rejection; an untested scope. |

## 2026-08-08 — global skills that are stack-specific

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-08 | [[vercel-skills]] | stack:next-vercel | **flagged** | 6 skills, **0 invocations** each, global | `deploy-to-vercel`, `vercel-cli-with-tokens`, `vercel-composition-patterns`, `vercel-optimize`, `vercel-react-best-practices`, `vercel-react-native-skills`, `vercel-react-view-transitions`. The 2026-08-07 rescope moved the *plugin* to project scope and left the *skills* global — a half-done fix reported as done. They load in every unrelated session. |
| 2026-08-08 | [[browser-skills]] | stack:browser-automation | **flagged** | `autobrowse`, `browser-trace`: 0 invocations since 2026-05-03 | Stack-specific, global. Belong in a repo that does browser work, or nowhere. |
| 2026-08-08 | [[db-test-skills]] | stack:erp-supabase | **flagged** | `database-migrations`, `e2e-testing`: 0 invocations | Plausibly right for the ERP stack — but that repo already has project-level `postgres-expert` and `playwright-e2e`, so these may be duplicates at the wrong scope. |
| 2026-08-08 | scope audit | global | **recorded** | 22 of 33 global skills are stack-agnostic; 11 are not | The rule is not "everything per-repo". Stack-agnostic tools belong global. The failure mode is a stack-specific tool at global scope: it taxes every session it cannot help. |

## Open questions

- **Restore 5 superpowers skills standalone?** `brainstorming`, `writing-plans`, `subagent-driven-development`, `systematic-debugging`, `finishing-a-development-branch` carried 138 of the 143 invocations. The repo clone was the problem, not the skills.
- **Does `ag-mcp` reduce `ag-grid` churn?** <project> `ag-grid` scope sits at **5.0 fix:feat** (9 feat / 45 fix) — the worst real scope in the repo — *with* an AG Grid MCP server installed. Either it is not being used, or it is not helping.