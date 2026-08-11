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
  A global "removed" erases that, and the transferable question is about the
  *kind* of codebase, not one repo.
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

## 2026-08-08 — rescope executed

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-08 | [[vercel-skills]] | stack:next-vercel | **rescoped** | 7 skills moved out of global into 2 repos | Now load only where a Vercel deploy exists. Completes the 2026-08-07 rescope, which moved the plugin and left the skills behind. |
| 2026-08-08 | [[browser-skills]] | stack:react-app | **rescoped** | `autobrowse`, `browser-trace` → 4 React repos | Browser automation is only meaningful where there is a UI to drive. |
| 2026-08-08 | [[db-test-skills]] | stack:data-pipeline | **rescoped** | `database-migrations`, `e2e-testing` → the migrations repo | Kept, not dropped — the migrations repo is where schema work happens. |
| 2026-08-08 | global harness | global | **reduced** | 33 → **22** global skills; 11 moved to the repos that use them | Every one of the 11 had 0 invocations while loading into every session. The rule holds: stack-agnostic global, stack-specific per repo. |

## 2026-08-09 — research methods reviewed, not installed

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-09 | [[karpathy-guidelines]] | global | **open** | 4 sections; 3 already covered by an installed always-on rule set | Only §3 *Surgical Changes* is new — "every changed line traces to the request", don't improve adjacent code. §2 and §4 restate rules already loaded every turn. §1 ("if unclear, stop and ask") **contradicts** the standing rule to act on a sensible default rather than stall. Adopting the block would buy one idea, three duplicates and one conflict. Candidate action: lift §3 into global rules, install nothing. |
| 2026-08-09 | [[karpathy-guidelines]] §3 | global | **adopted** | 1 of 4 sections lifted; 0 files installed | *Surgical Changes* — every changed line traces to the request, don't improve adjacent code, remove only the orphans your own edit created. Written into global rules in ~6 lines. The other three sections stay out: two duplicate always-on rules already loaded, one was rejected below. Adoption without installation — the idea moved, the package did not. |
| 2026-08-09 | [[karpathy-guidelines]] §1 | global | **rejected** | 0 installed rules carry ask-first; 2 state the opposite | *Think Before Coding* asks the agent to stop and ask whenever something is unclear. Conflicts with the standing rule to act on a sensible default and state the assumption. Resolved in favour of acting: an agent that stops on every ambiguity converts a 1-turn task into 3 and pushes its own judgement onto the user. Ambiguity gets a stated assumption, not a question. Blocking questions stay reserved for work that would be unsafe or useless if the guess is wrong. Note the failure mode this accepts: occasional confident work in the wrong direction, cheaper to redo than to prevent. |
| 2026-08-09 | shannon-method | global | **recorded** | 9 habits transfer, 6 invert | Kept as prose in `wiki/patterns/shannon-method.md`, not a skill — zero context cost, promoted only if reached for by hand. Two habits are *actively harmful* to an agent: "three ideas in parallel" produces unreviewable scattered diffs, and "discovery matters, write-up is an afterthought" produces silent work. Both are downstream of Shannon being a principal with no reviewer. |

## 2026-08-10 — first weekly review

First pass of `skills/tool-review`. Two proposals in the original draft were
withdrawn on the user's objection: both judged tools inside windows too short to
see anything — `adhd` installed three days earlier, `superpowers` removed three
days earlier. The rules that came out of that are in the skill, and the review
graded itself accordingly: 3 proposals, 1 accepted outright, 2 rewritten.

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-10 | [[framework-mcp]] | stack:erp-supabase | **removed** | 0 calls in 2,396 sessions; declared for two project paths that left `repos.txt` today | Project-scoped MCP server for a terminated project — vendor name withheld, it is in `.leakpatterns`. A server for a stack that no longer exists cannot become useful later, so no trial is owed. Config edit is the user's — `~/.claude.json` still declares it, and the next `reconcile.py` will disagree with this row until it does not. |
| 2026-08-10 | [[colab-mcp]] | stack:data-science | **removed** | 0 calls in 2,396 sessions; its project is not in `repos.txt` | Same class: declared for a project this brain does not watch. Removing on a zero is only safe because the *project* is gone, not because the count is low. |
| 2026-08-10 | [[find-skills]] | global | **removed** | 0 invocations since 2026-03-17; `tool-decisions` declares the same trigger phrase | **Superseded, not unused.** It answers "what could I install" — which `discover.sh` already does — while `tool-decisions` claims `"is there a skill for X"` in its own description and checks the ledger first. Two skills competing for one phrasing; the more specific one wins. Recorded as supersession so the next reader sees why it lost rather than assuming it was bad. |
| 2026-08-10 | [[matt-pocock-skills]] | global | **flagged** | 8 skills, 0 invocations each; 1,448 cleanup-shaped and 778 test-shaped sessions of 2,391 in 30 days | Supersedes the 2026-08-08 flag with a diagnosis instead of a verdict. Zero use has four causes and only one justifies removal: no demand, a description the model never matched, a user who never knew the tool was there, or one who never learned when to reach for it. Demand is plainly present, so cause 1 is out — and causes 3 and 4 have never been tested even once. Trial queue opened; no removal until each has been tried deliberately. |
| 2026-08-10 | [[grill-me]] | global | **open** | 0 invocations in 2,462 sessions; 1,306 brainstorm-shaped sessions in 30 days | Pulled out of the removal list. It is the untried substitute for a capability removed three days ago, and the first draft of this review proposed deleting it *and* re-adopting what it substitutes for — incoherent. **An untried alternative blocks the decision in both directions.** Trial on the next plan worth stress-testing. Re-evaluate 2026-08-21. |
| 2026-08-10 | [[superpowers]] | global | **open** | removed 2026-08-07 — 3 days; 1,306 brainstorm / 613 plan / 1,280 debug-shaped sessions in 30 days | Proposal to restore 5 skills standalone was **withdrawn, not rejected**. Nobody misses a tool in three days, and the substitute already installed has never been tried. This is the removal-side blind window: after an install, zero invocations mean nothing for 14 days; after a removal, no pain means nothing either, and only the first has an automatic guard. Watch item. Re-evaluate 2026-08-21. |
| 2026-08-10 | [[claude-mem]] | global | **recorded** | 951 of 2,396 sessions covered (~40%); 8,126 prompts, 6,444 summaries, 32,114 observations in a plain SQLite file | Read as **optional enrichment, never the store of record.** Coverage is the disqualifier: a 60% hole would hide findings without saying so. Trust splits three ways — `user_prompts` is verbatim and better than any regex, `session_summaries` point at sessions worth opening, `observations` are another model's judgement and are not evidence. The dependency stays soft: stdlib `sqlite3` reads the file whether or not the plugin runs, so this row never blocks removing it. |
| 2026-08-10 | braintool `SessionEnd` hook | global | **adopted** | covers 2,396 of 2,396 sessions vs 951; 0 model calls | `bin/session_log.py` prints loops, rework, failures and which skills fired as a session closes, and appends the same to `inventory/sessions.jsonl`. Chosen over reusing an existing capture because everything shown is countable — no model call, so it costs nothing and covers everything. The line that earns it is `skills: none fired`, which is the awareness gap made visible at the only moment anyone cares. First measurement from it: **2,306 of 2,391 sessions (96%) invoked no skill at all.** |

## 2026-08-11 — the instrument was wrong

The first weekly review was run properly for the first time — 15 sessions read
in full, by an agent with no memory of writing any of this. Its most useful
finding is about the measuring tool, not the tooling: **a zero the scanner never
computed reads exactly like a measured one.** Same class as `BLOCKED` shipping
as `PASS`, and it contaminated rows written the day before.

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-11 | reconcile RE_MCP | global | **fixed** | `[a-zA-Z0-9_]` excluded `-`; `ag-mcp` read 0 on **11 real calls**, context-mode invisible on **3,539** | Every MCP server with a hyphen in its name matched nothing and was reported `NEVER CALLED`. One character. The damage is not the bug, it is that the output was indistinguishable from a real measurement — so a false zero was written into this ledger as evidence and into the open questions as a premise. |
| 2026-08-11 | [[colab-mcp]] | stack:data-science | **superseded** | supersedes 2026-08-10: its evidence was never computed | The **decision stands** — the project is gone, which is the reason that carries it. The *evidence* was false: `colab-mcp` carries a hyphen, so "0 calls in 2,396 sessions" was a number the scanner could not produce. Recorded rather than edited, because a ledger that quietly repairs itself teaches nothing. [[framework-mcp]]'s zero was real; its name has no hyphen. |
| 2026-08-11 | [[ag-mcp]] | stack:erp-supabase | **open** | 11 calls, 5 sessions, last 2026-08-07 — not 0 | The standing open question asked whether it was "not being used, or not helping", on a zero that never existed. It *is* used, thinly. With `ag-grid` at 5.0 fix:feat and grid views recurring in the rework table, the question is now answerable and worth asking again — but 11 calls is too thin to judge either way. Re-ask after the counter has run a full week. |
| 2026-08-11 | braintool `SessionEnd` hook | global | **fixed** | 7 rows for 2 sessions; one session logged 5 times | The hook fires on clear and on resume, and the log appended unconditionally. Adopted yesterday as the review's ground truth, wrong within a day. Now one row per session, and the existing file compacted 10 → 4. Every ratio computed from it before today was weighted by how often a session got interrupted. |
| 2026-08-11 | [[framework-mcp]] | stack:erp-supabase | **open** | still declared in the terminated repo's own `.mcp.json`; unapproved, so its tools are dead | The `~/.claude.json` entries are gone, but the repo still sits on disk carrying its own declaration. Textbook [[plugin-removed-artifacts-remain]]: removing the config does not remove what was written elsewhere. Harmless while unapproved. Closes when the directory goes. |

**Method note.** The review that found all of this read sessions; the review that
wrote the bad evidence read tables. Both used the same data. The difference is
worth more than any single row above.

## 2026-08-11 — a rule with no way back in

Read of a single 8.2MB session, prompted by the user reporting it as unlike
anything they had seen. The finding is not about a tool that was installed. It
is about which instructions survive a compaction and which do not.

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-11 | `rules-after-compact` hook | global | **adopted** | rules last present `2026-08-10T15:21:08`; absent across a 734k→17k compaction while ~52KB of plugin hooks re-injected at `17:06:50`; 63 unsupervised minutes followed | A `/compact` writes a summary answering *"what are we doing"*. Goals survive it; **prohibitions do not**. At the boundary, caveman (902b), ponytail (8,567b), context-mode (16,531b) and claude-mem (23,946b) all re-announced themselves — because each owns a `SessionStart` hook. The *Surgical changes* rule appears exactly twice in 8.2MB, both at session start 26 hours earlier, and never again. What followed: five unrequested changes shipped to production in one 63-minute turn, four reverted, one issue reopened, ~2.5h lost. **Plugins survive compaction because they have a mechanism. Rules had none.** ~40 lines in `~/.claude/hooks/`, reading the sections straight out of `CLAUDE.md` so it cannot drift, silent on every non-compact start. |
| 2026-08-11 | braintool scope | global | **recorded** | 1 hook adopted, 0 files added to this repo | The hook was deliberately **not** shipped from braintool. This repo observes — `reconcile.py` reads, `session_log.py` records, and the README promises it never mutates. A hook that changes what the agent *does* mid-session is a harness change, not an audit tool, and shipping it here would blur the one line that makes the ledger worth reading. The rules are also personal and this repo is public. So: the harness holds the mechanism, the ledger holds the decision and the evidence. That split is the answer to "should braintool ship behaviour", and it is no. |

**What the counters could not have found.** Every guardrail in that session
passed — dry runs, assertions, typecheck, 1,455 tests — because they all test
whether a change is *correct*, never whether it was *requested*. The expensive
failure produced **zero errored tool results**. `demand.py` ranks by errors,
loops and rework; on its own numbers this was a productive day.

## 2026-08-11 — hooks, the surface nobody was counting

Asked what braintool actually looks at, the answer turned out to be "nine
surfaces properly and hooks barely" — on the same day hooks were shown to be the
mechanism that decides what survives a compaction.

| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-08-11 | reconcile hooks | global | **fixed** | 3 hooks inventoried on a machine running **16**; one plugin script at **7,324 firings** unseen; this repo's own hook reported `MISSING BINARY` while firing 17 times | Four separate false verdicts, all the same shape as the `RE_MCP` zero found this morning. (1) The first token of the command was read as the hook, so `python3 …/session_log.py` resolved to `python3` and every interpreter-launched hook read as broken. (2) Only `settings.json` was read, while plugins declare hooks in three other shapes — `hooks/hooks.json`, `plugin/hooks/hooks.json`, and inside `plugin.json`. (3) A path built at run time through shell variables was called MISSING rather than unknown. (4) Hooks carried `observable: reachability` — does the file exist — while every firing sat in the transcripts uncounted. Hooks now report **firings**, and the two cases that genuinely cannot be measured say so instead of printing 0. |
| 2026-08-11 | braintool scope | global | **recorded** | 10 surfaces named in the README, 1 of them previously unmeasured | Scope written down for the first time: skills, **hooks**, MCP servers, subagents, plugins, project tooling, settings, usage, behaviour, outcomes. Each activates differently and rots differently, so each is read separately — and the reason to name them is that the one nobody had enumerated is the one that was broken. Hooks fire unconditionally in every session, so a dead one is pure tax and a live one changes behaviour invisibly. That makes them the surface most worth counting and the easiest to miss. |

**Still not measurable, and now labelled as such.** A hook that runs a binary
(`rtk hook claude`) leaves no script name in the transcript, so it reads *not
measurable*, never 0. A hook resolving its own path at run time reads *declared*.
Both are the same rule this ledger keeps relearning: report the unknown as
unknown, or the next reader will spend it as evidence.

## Open questions

- **Restore 5 superpowers skills standalone?** `brainstorming`, `writing-plans`, `subagent-driven-development`, `systematic-debugging`, `finishing-a-development-branch` carried 138 of the 143 invocations. The repo clone was the problem, not the skills.
- **Does `ag-mcp` reduce `ag-grid` churn?** <project> `ag-grid` scope sits at **5.0 fix:feat** (9 feat / 45 fix) — the worst real scope in the repo — *with* an AG Grid MCP server installed. Either it is not being used, or it is not helping.