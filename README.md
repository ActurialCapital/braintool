<p align="center">
  <img src="assets/braintool-banner.png" alt="braintool" width="100%">
</p>

<p align="center">
  <strong>An agent-maintained wiki of your AI tooling — kept honest against what is actually installed and actually used.</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#core-ideas">Core ideas</a> ·
  <a href="#commands">Commands</a> ·
  <a href="#privacy">Privacy</a> ·
  <a href="#obsidian">Obsidian</a> ·
  <a href="#faq">FAQ</a>
</p>

<p align="center">
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-4f46e5?style=flat-square"></a>
  <img alt="python" src="https://img.shields.io/badge/python-3.10%2B-4f46e5?style=flat-square&logo=python&logoColor=white">
  <img alt="dependencies" src="https://img.shields.io/badge/dependencies-none-6366f1?style=flat-square">
  <img alt="storage" src="https://img.shields.io/badge/storage-plain%20markdown-6366f1?style=flat-square&logo=markdown&logoColor=white">
  <img alt="obsidian" src="https://img.shields.io/badge/vault-Obsidian%20ready-7c3aed?style=flat-square&logo=obsidian&logoColor=white">
  <br>
  <img alt="pattern" src="https://img.shields.io/badge/pattern-LLM%20Wiki-818cf8?style=flat-square">
  <img alt="scope" src="https://img.shields.io/badge/decisions-scoped%20by%20stack-818cf8?style=flat-square">
  <img alt="privacy" src="https://img.shields.io/badge/privacy-local%20by%20default-10b981?style=flat-square&logo=gnuprivacyguard&logoColor=white">
  <img alt="PRs" src="https://img.shields.io/badge/PRs-welcome-10b981?style=flat-square">
</p>

---

## A second brain, for your tooling

Andrej Karpathy's [**LLM Wiki**](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
describes a personal knowledge base an LLM maintains for you: you drop raw
material into a folder, the model compiles it into structured, interlinked
markdown, and you browse the result. The agent is the librarian; you are the
curator.

**braintool applies that pattern to the harness itself** — your skills, plugins,
MCP servers, hooks, and agent frameworks.

The difference is where the raw material comes from. A reading wiki ingests
articles you clip. This one ingests **your machine**: what is installed, what
actually gets invoked, what still connects, and what your commit history says
about whether any of it helped. A reading wiki's facts are stable — a paper says
what it says forever. These facts **expire**: versions bump, repos get abandoned,
CVEs land, a plugin breaks against a new release.

So the loop is not *ingest → structure → browse*. It is **reconcile**: every run
diffs what the wiki claims against what is actually on disk, and the disagreement
is the finding.

---

## The problem

An agent harness grows by accretion. A skill here, a plugin there, an MCP server
for a project finished last quarter. Each one costs context in **every session**,
adds surface area, and creates a cleanup nobody schedules.

Nothing tells you when a tool stops earning its place. Uninstalling a plugin
disables it but leaves behind whatever it wrote into your config directory, and
those leftovers keep loading forever. The bill is paid silently, so it never
comes due.

Meanwhile the public catalogs — awesome-lists, plugin directories, template
registries — all answer the same question: *what exists?* None of them can
answer the two that matter:

> **What do I actually have, and is any of it helping?**

A first run on a single machine surfaced four installed frameworks with **zero
invocations between them**, one MCP server silently unapproved for weeks — hiding
32 working tools — and ~17MB of orphaned artifacts from plugins removed months
earlier. No catalog could have found any of it, because none of it is about what
exists. It is about what you installed and forgot.

---

## What it does

```
  reconcile ──►  what is installed, what connects, what nothing calls
      │
      ▼
  churn     ──►  fix:feat over time — did the work land right the first time?
      │
      ▼
  discover  ──►  candidates from your GitHub stars (only when shopping)
      │
      ▼
  gate      ──►  security scan + fit check against the stack in front of you
      │
      ▼
  ledger    ──►  the decision, with evidence — including every no
```

Plain markdown in a git repo. No database, no service, no dependencies beyond
Python 3 and `git`. Readable in any editor, browsable as an
[Obsidian](https://obsidian.md) vault, diffable in review.

---

## Quick start

```bash
git clone https://github.com/ActurialCapital/braintool
cd braintool

cp repos.txt.example repos.txt          # the repos you ship, + their stack type
cp .leakpatterns.example .leakpatterns  # private names that must never publish
python3 bin/leakcheck.py --install      # pre-commit guard

./bin/weekly.sh                         # the hygiene pass
```

The first run writes `inventory/`, generates the wiki, and prints its findings.
Nothing is installed, removed, or changed on your machine — it only reads.

**Optional**, for the security gate: a [Snyk](https://app.snyk.io/account) token
in `.env` as `SNYK_TOKEN=…`. The scanner itself needs no install; `uvx` fetches
it on demand.

---

## Core ideas

### 1. The ledger is the product

`ledger.md` records every adopt / reject / remove / rescope decision with the
evidence behind it.

**The noes are worth more than the yeses.** Catalogs already list what is
available. Nothing anywhere records what *you* tried, dropped, and why — and that
record is the only thing that makes the next decision better than the last.

```markdown
| Date | Tool | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|---|
| 2026-01-14 | [[some-framework]] | global | removed | 0 invocations in 2,400 sessions | 33 agent descriptions loaded into every session for a framework nothing ever called. |
```

`evidence` must be a number or a file path. Never an opinion.

### 2. Decisions are scoped to a stack *type*

A tool can be right for one kind of codebase and wrong for another. A heavy
planning framework suits greenfield work and gets in the way of a mature system.
A deploy plugin is essential to one stack and dead weight in every other session.

A single global verdict erases that, so `scope` holds a **stack type**:

```
global              → helps regardless of what you are building
stack:next-vercel   → only where that deploy target exists
stack:data-science  → notebooks, dataframes, experiments
stack:trading       → strategy and backtest work
```

The same tool can carry two rows with opposite verdicts. **Both are true.**

Scope is a stack type rather than a repo name for two reasons: repo names are
usually private, and *"is this good for a Next.js app on Vercel"* transfers to the
next repo of that kind, while *"is this good for my-project-42"* does not.

This also decides **where a tool gets installed**:

| Verdict | Install location |
|---|---|
| helps every stack | your global agent config |
| helps one stack | that repo's `.claude/` or `.mcp.json` |
| helps nowhere | a ledger row saying no |

That middle row is the one people skip, and skipping it is how a harness fills up
with tools that help one repo and tax every other session.

### 3. "Not measurable" is a first-class answer

The hardest bugs in this project were the tool reporting confidence it had not
earned. Three separate wrong findings came from one wrong assumption — that usage
means *invocation count*:

| Activation | Why the count lies |
|---|---|
| hook | fires on every matching event, never appears as an invocation |
| plugin-activated | injected at session start, not called |
| user-only | the agent is *forbidden* from calling it; zero is a rule, not a verdict |
| project-scoped | usage counters are machine-wide, so they cannot be attributed per repo |

So every row carries `activation` and `observable`:

```json
{"name": "some-hook",  "activation": "hook",      "observable": "reachability", "value": true}
{"name": "some-skill", "activation": "user-only", "observable": "none",         "value": null}
{"name": "other",      "activation": "model",     "observable": "invocations",  "value": 0}
```

`observable: none` means **this cannot be seen from here** — which is not evidence
of disuse. The same rule governs the security gate, where a scanner that examined
nothing returns `BLOCKED`, never `PASS`.

### 4. Churn is the outcome metric

Everything else is a proxy. The honest question is whether work lands right the
first time, and conventional commits already answer it:

```
feat(parser): add streaming mode
fix(parser): handle empty chunks       ← the tax
fix(parser): off-by-one on final read
fix(parser): restore backpressure
```

`churn.py` computes **fix:feat** per repo and per scope, appends it to
`inventory/churn.jsonl`, and `--history` prints the series with ledger decisions
overlaid on one timeline. A scope far above the repo average is a question, not a
verdict: is the tooling for that area unused, or unhelpful? Both answers are
worth having.

It does **not** claim causation. Decisions and outcomes are shown together;
reading them is your job.

### 5. Look at everything, adopt almost nothing

`discover.sh` sweeps your GitHub stars into a shortlist. A typical run turns
~1,000 stars into ~100 candidates and adopts **zero**. That ratio is the point.

Popularity is not fit. Of the frameworks removed in this project's own first
audit, three were current, popular, and actively maintained. The failure was
never staleness.

---

## Commands

| Command | What it does |
|---|---|
| `./bin/weekly.sh` | The hygiene pass: reconcile → churn → pages → lint |
| `./bin/discover.sh [--refresh]` | Sweep starred repos into `inventory/candidates.md` |
| `python3 bin/reconcile.py` | Inventory installed tools, global and per repo |
| `python3 bin/churn.py <repo>… [--record]` | fix:feat per repo and scope |
| `python3 bin/churn.py --history` | The outcome series with decisions overlaid |
| `python3 bin/gate.py <path> --stack <type>` | Security scan + fit check |
| `python3 bin/pages.py [--force]` | Regenerate wiki pages from the ledger |
| `python3 bin/lint.py [--all]` | Broken wikilinks, orphans, stale pages |
| `python3 bin/leakcheck.py [--install]` | Block private names from publishing |

Hygiene and discovery are deliberately separate. Hygiene finds dead tooling every
time it runs; discovery mostly produces reading. They do not deserve the same
cadence.

---

## Layout

```
braintool/
├── ledger.md              every decision + evidence          ← the product
├── repos.txt              your repos and their stack types   (gitignored)
├── .leakpatterns          names that must never publish      (gitignored)
├── bin/
│   ├── weekly.sh          hygiene pass
│   ├── discover.sh        star sweep
│   ├── reconcile.py       installed vs. observable
│   ├── churn.py           fix:feat, recorded over time
│   ├── sweep.py           stars → candidates
│   ├── gate.py            security + fit
│   ├── pages.py           ledger → wiki pages
│   ├── lint.py            vault health
│   └── leakcheck.py       privacy guard
├── skills/
│   └── tool-decisions/    the agent-facing door into the ledger
├── wiki/
│   ├── tools/             one page per DECIDED tool     (public)
│   ├── local/             one page per INSTALLED tool   (gitignored)
│   ├── stacks/            one page per repo + MAP.md    (gitignored)
│   └── patterns/          recurring lessons             (public)
└── inventory/             generated ground truth        (gitignored)
```

Two folders hold tool pages and never the same name twice. **Public pages come
from the ledger** — decisions, safe to share. **Local pages come from disk** —
facts about your machine. Every `[[link]]` resolves, and no private tool name is
ever published.

---

## Privacy

This repo maps a machine and the repos on it. The sensitive data is not
incidental — it is the input. So:

- **Local data is private by default.** `.gitignore` is an allowlist, not a
  blocklist. Anything new under `inventory/`, `wiki/local/` or `wiki/stacks/`
  stays local unless explicitly un-ignored. A blocklist makes every new output
  file public by default, which is how leaks happen twice.
- **Repo paths live in `repos.txt`**, never in a committed script.
- **`leakcheck.py` blocks the commit.** It reads `.leakpatterns` — itself
  gitignored, since it holds the very names it protects — and fails on any tracked
  or staged file that matches.

```bash
python3 bin/leakcheck.py --install    # runs whether or not you remember
```

Curate `.leakpatterns` by hand. Auto-globbing every directory name flags public
repos and your own account, and a guard that cries wolf gets switched off.

---

## Obsidian

The wiki is plain markdown with `[[wikilinks]]`, so [Obsidian](https://obsidian.md)
reads it with no plugin, no import, and no lock-in. *Open folder as vault* → pick
the repo.

What it buys you:

- **Backlinks** answer *which stacks use this tool* — open any tool page and look
  at the bottom.
- **Graph view** clusters per repo, because each stack page links its own tools.
  Orphaned clusters become visible: a dense island with no edge to any active
  stack is exactly the rot you are hunting.
- **`wiki/stacks/MAP.md`** is the entry point — every repo, its stack type, its
  tool count.

Generated pages carry a marker:

```
─ generated ────────────  rewritten every run from the ledger
<!-- marker -->
─ your notes ───────────  never touched
```

Edit freely below the marker. To change what is above it, edit `ledger.md` — the
page is a projection of it.

`lint.py` reports broken wikilinks and orphans, because a wiki with nothing
watching it rots quietly. This one launched with 45 broken links out of 46.

---

## Wiring it into your agent

A wiki nothing reads is a notebook. `skills/tool-decisions/` is the door — an
[agent skill](https://agentskills.io) that loads only when the task is about
adding, removing, or evaluating tooling, and makes the agent read the ledger
before forming an opinion.

```bash
ln -s "$PWD/skills/tool-decisions" ~/.claude/skills/tool-decisions
```

Deliberately a skill rather than a line in your always-loaded instructions: this
matters a handful of times a year, and always-loaded context is charged in every
session forever.

---

## Patterns

Recurring lessons, each with occurrences and evidence:

- [[plugin-removed-artifacts-remain]] — uninstalling disables a plugin; it does
  not remove what the plugin wrote into your config directory.
- [[acceptance-test]] — the standing test of whether this system works at all.

---

## Design principles

1. **Newer is not better.** Fit fails first, and fit is free to check.
2. **Removals are worth more than additions.** Anyone can list what is available.
3. **Look at everything, adopt almost nothing, write down every no.**
4. **Facts expire.** Every page carries `verified_at`. Unverified is stale.
5. **Ground truth beats the catalog.** The wiki is wrong the moment it disagrees
   with disk.
6. **Never report a verdict you did not earn.** *Not measured* is an answer.
7. **Generated is facts; hand-written is judgement.** Never let a script write the
   second kind.

---

## FAQ

**Does it change anything on my machine?**
No. `reconcile.py` only reads. Adding or removing tools is always your action —
the loop produces evidence and a recommendation, never a mutation.

**Does it work with agents other than Claude Code?**
The concepts are agent-agnostic; the collectors are not. `reconcile.py` reads a
config directory and session transcripts, so pointing it at another agent means
rewriting `scan_usage()` and `installed_skills()` — roughly 60 lines. The ledger,
scoping, gate, churn, and wiki are unchanged.

**Why not a database?**
Because the artifact should outlive the tool. Markdown in git is diffable,
reviewable, greppable, and readable in fifty years. A schema migration for a
personal knowledge base is a cost with no matching benefit.

**Why does discovery find so much and adopt so little?**
Because that is correct. The scarce resource is not tools, it is attention and
context budget. If a sweep produces adoptions often, the filter is too loose.

**Can I run it in CI?**
Only the discovery half. Reconciliation reads your local agent config, which no
runner has. Run hygiene locally — that is where the ground truth lives.

**What if I do not use conventional commits?**
Churn degrades to a non-conventional bucket and tells you little. Either adopt
`feat:`/`fix:` prefixes, or replace `churn.py` with an outcome metric your history
can support — revert rate, time-to-green, incident count.

**How is this different from Karpathy's LLM Wiki?**
Same pattern, different input and one extra loop. The LLM Wiki ingests material
you clip; this ingests your machine. And because tooling facts expire, it adds
reconciliation — the wiki is checked against disk on every run, and a claim that
no longer matches reality is a finding rather than a page.

---

## Contributing

Issues and PRs welcome. The bar for a new collector or metric is the same bar the
project applies to tools: it has to earn its context. If it cannot say *how* it
knows something — and admit when it cannot know — it does not go in.

## License

[MIT](LICENSE) — fork it, rename it, make it yours. Inspired by Andrej Karpathy's
[LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

---

<p align="center">
  <sub>Look at everything. Adopt almost nothing. Write down every no.</sub>
</p>
