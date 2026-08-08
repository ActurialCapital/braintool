---
name: tool-decisions
description: Consult the tooling ledger before adding, removing, or evaluating any agent tool — a skill, plugin, MCP server, hook, or agent framework. Use when the user says install/add/try/adopt/drop/remove/clean up about tooling, asks "is there a skill for X", "should I use X", "what's in my setup", or points at a repo as a candidate. Also use before editing ~/.claude (settings.json, skills/, agents/, plugins) or any .mcp.json. Checks whether the thing was already decided on, already installed, or already removed for a reason, then records the outcome. Do not use for ordinary code work in a project.
---

# Tool decisions

The harness is not free. Every skill, plugin, and MCP server costs context in
every session, adds surface area, and creates a future cleanup. A tooling
decision made from memory repeats mistakes that are already written down.

**Brain:** `~/GitHub/ActurialCapital/braintool`

## Before answering, read the ledger

```bash
BRAIN=~/GitHub/ActurialCapital/braintool
grep -i "<tool-name>" $BRAIN/ledger.md
```

The ledger records adopt / reject / remove decisions with evidence. **The noes
are the valuable part** — public catalogs already list what exists; only this
records what was tried and dropped, and why.

If the tool appears there, lead with that. "You removed this on <date> because
<reason>" is more useful than a fresh opinion.

## Every verdict is scoped — never answer globally

The ledger's `scope` column holds a **stack type**, not a repo name. The same
tool is often right for one kind of codebase and wrong for another: heavy
planning frameworks suit greenfield work and not a mature ERP; a deploy plugin
is essential to one stack and dead weight in every other session.

So the question is never "is this good?" — it is **"good for which stack?"**

```bash
grep -E '^\| .*\| stack:' $BRAIN/ledger.md   # scoped decisions
cat $BRAIN/wiki/stacks/MAP.md                # which repo is which stack type
```

Match the repo you are working in to its `stack_type` (in `repos.txt` and each
stack page's frontmatter), then read the rows for that type **plus** the global
rows. A tool can carry two rows with opposite verdicts in different scopes;
both are true.

That also decides **where it gets installed** if adopted:

| Verdict | Install location |
|---|---|
| useful in every stack | `~/.claude` — global |
| useful in one stack | that repo's `.claude/` or `.mcp.json` |
| useful nowhere | a ledger row saying no |

The middle row is the one that gets skipped, and skipping it is how a harness
fills with tools that help one repo and tax every other session.

## Then check what is actually installed

```bash
cd $BRAIN && python3 bin/reconcile.py
```

Writes `inventory/inventory.json` (local, gitignored). Answers:

- is it already installed?
- has anything ever invoked it?
- does the MCP server actually connect, or is it declared-but-unapproved?

**Never conclude "unused" from an invocation count of zero.** Hook-activated
tools — rtk, caveman, ponytail, context-mode — never appear as `Skill` calls and
are running constantly. `reconcile.py` classifies by activation mode for exactly
this reason. Read the `status` column, not the number.

## For something new, gate it before adopting

```bash
python3 bin/gate.py <local-path-or-url> --stack <stack>
```

Three verdicts, and the third is not a warning:

| Verdict | Meaning |
|---|---|
| `PASS` | scanner ran, examined the thing, found nothing |
| `CONCERNS` | scanner ran and found something — read it |
| `BLOCKED` | the scanner **did not examine anything**. Not clean. Do not adopt. |

A raw `git clone` often produces BLOCKED because the scanner wants the installed
layout (`~/.claude/skills/<name>`), not a repo root. That is inconclusive, not
safe. Snyk's Feb 2026 audit found a 36% flaw rate across 3,984 skills and 76
with live malicious payloads. A star count is not a safety signal.

Fit fails first and costs nothing: check `wiki/stacks/<stack>.md` before running
any scan. A tool that does not match the stack is a no regardless of quality.

## Record the decision — including the no

Append a row to `ledger.md`:

```markdown
| YYYY-MM-DD | [[name]] | adopted/rejected/removed/rescoped | <number or path> | <why> |
```

`evidence` must be a number or a file path, never an opinion. Then:

```bash
python3 bin/pages.py && python3 bin/lint.py
```

`pages.py` regenerates `wiki/tools/<name>.md` from the ledger. Anything written
below the marker in a page is the user's and is preserved. `lint.py` catches
broken wikilinks before they accumulate.

## When removing, the tool is not the artifacts

Disabling a plugin does not remove what it wrote into `~/.claude`. This has
happened four times on this machine — superpowers, gsd, sentrux, failed installs
— for ~17.7M and 230+ phantom slash commands loading into every session.

After any removal:

```bash
ls ~/.claude/commands ~/.claude/agents 2>/dev/null   # orphaned artifacts?
grep -i "<tool>" ~/.claude/settings.json             # orphaned hooks?
find ~/.claude -maxdepth 2 -iname "*<tool>*"         # orphaned state?
```

**But check `git ls-files` before deleting anything inside a repo.** Not
everything named after the tool belongs to it: `docs/superpowers/` held 173
tracked files cited from production source. Config artifacts are disposable;
work product wearing the tool's name is not.

## Full weekly pass

```bash
cd $BRAIN && ./bin/weekly.sh          # reconcile, churn, sweep, pages, lint
./bin/weekly.sh --refresh             # also re-pull starred repos
```

`inventory/candidates.md` holds the shortlist. Nothing there is adopted — each
entry still needs a gate and a ledger row.

## The standing bias

Look at everything, adopt almost nothing, write down every no. Of the frameworks
removed so far, three were current, popular, and actively maintained. The
failure was never staleness — it was fit.
