# braintool

An agent-maintained wiki of **my** AI tooling — skills, plugins, MCP servers, hooks,
harness — that keeps itself honest against what is actually installed and actually used.

Built on the [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
Browse it in [Obsidian](https://obsidian.md): plain markdown with `[[wikilinks]]`, so the
graph view and backlinks come free and nothing in this repo depends on Obsidian.

## Why this is not another awesome-list

Public catalogs (`awesome-claude-skills`, aitmpl.com, claudepluginhub) tell you what
**exists**. None of them know what **you have installed**, whether it still connects,
or whether anything ever calls it.

That gap is expensive. A single audit on 2026-08-07 found four frameworks installed,
loading into every session, and invoked **zero times** between them — plus one MCP
server silently unapproved for weeks, hiding 32 working tools.

## The loop

```
  reconcile  ──►  what is installed, what connects, what nothing calls
      │
      ▼
  sweep      ──►  new candidates from stars + registries
      │
      ▼
  gate       ──►  security scan (Snyk Agent Scan / mcp-scan) + fit vs my stacks
      │
      ▼
  PR         ──►  proposed adds/removes as a reviewable diff
      │
      ▼
  ledger     ──►  merge or close IS the outcome signal; it trains the next fit score
```

Nothing auto-commits. The merge/close decision is the feedback.

## What gets measured

Exact, already on disk:

- invocations + last-used, per skill / MCP server / subagent (from `~/.claude/projects/*.jsonl`)
- context cost — description bytes × sessions loaded
- MCP health — connects / fails / declared-but-unapproved
- **churn** — `fix:feat` ratio per repo and per scope, the honest outcome metric

Deliberately not measured: "usability", "efficiency". They are unfalsifiable without
an A/B harness, and a trigger-optimisation loop run on 2026-08-07 proved the point —
it could not score a skill whose success looks like an absence.

### The blind spot that breaks naive scoring

`caveman`, `ponytail`, `rtk`, `context-mode` show **0 skill invocations** and are all
running right now. They activate through hooks, not `Skill` calls. Any score that
counts invocations alone deletes the best-integrated tools first. `reconcile.py`
classifies by activation mode for exactly this reason.

## Usage

```bash
python3 bin/reconcile.py                      # inventory + findings
python3 bin/churn.py ~/code/*                 # fix:feat per repo and scope
python3 bin/sweep.py --refresh                # starred repos -> candidates
python3 bin/gate.py <repo> --stack <stack>    # security + fit, before adopting
```

**Local output is not published.** `inventory/inventory.*`, `inventory/churn.md`
and `wiki/stacks/*` are gitignored — an inventory is a map of one machine and a
stack page is a map of a private codebase. Only the tooling, the ledger, and the
patterns are public.

`bin/gate.py` needs `SNYK_TOKEN` in the environment (https://app.snyk.io/account).
Without it the gate returns **BLOCKED**, by design — an unauthenticated scan is
not a clean scan. Put it in this repo's `.env`, not in a project's.

## Layout

```
inventory/    reconcile.py output — ground truth, regenerated, never hand-edited
wiki/
  tools/      one page per tool: what it is, verified_at, security verdict, fit
  stacks/     project profiles — what each codebase actually uses
  patterns/   recurring lessons, e.g. "plugin removed, artifacts remain"
ledger.md     every adopt/reject/remove decision + evidence  ← the product
```

## Principles

1. **Newer is not better.** Of four frameworks removed on day one, three were current
   and actively maintained. The failure was fit, never staleness.
2. **Removals are worth more than additions.** Anyone can list what is available.
3. **Look at everything, adopt almost nothing, write down every no.**
4. **Facts expire.** Every page carries `verified_at`. Unverified is stale by default.
5. **Ground truth beats the catalog.** The wiki is wrong the moment it disagrees with disk.

## Wiring it into the agent

A wiki the agent never reads is a notebook. `skills/tool-decisions/` is the door:
it loads only when the task is about adding, removing, or evaluating tooling,
and it makes the agent read `ledger.md` before forming an opinion.

```bash
ln -s "$PWD/skills/tool-decisions" ~/.claude/skills/tool-decisions
```

Deliberately a skill rather than a `CLAUDE.md` line: this matters ten times a
year, not in every message, and `CLAUDE.md` is loaded into every session forever.

## Patterns

Recurring lessons, each with occurrences and evidence:

- [[plugin-removed-artifacts-remain]] — uninstalling disables a plugin; it does
  not remove what the plugin wrote into `~/.claude`. Four occurrences, ~17.7M.
- [[acceptance-test]] — the standing test of whether this system works at all.
