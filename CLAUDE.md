# CLAUDE.md

Rules for working **on** braintool. For using the ledger from another repo, see
`skills/tool-decisions/SKILL.md` instead — that is the consumer-facing skill.

## What this is

A wiki of AI tooling decisions, kept honest against what is actually installed
and actually used. `bin/` scans the machine and writes `inventory/`, `wiki/` and
`MAP.md`. `ledger.md` is written by hand. Everything is plain markdown with
`[[wikilinks]]`; Obsidian is a lens over it, never a dependency.

## The ledger is append-only

**Never edit a past row.** A decision that turned out wrong gets a *new* row that
supersedes it, on a new date. The record of what was believed and when is the
only thing that makes the next decision better than the last one — rewriting it
destroys the product.

## `scope` is a stack type, never a repo name

`stack:next-vercel`, `stack:erp-supabase`, `stack:greenfield`. The transferable
question is about the *kind* of codebase. Same tool, different stack, opposite
verdict is normal — write two rows, both true. Repo paths live in `repos.txt`.

## Privacy is mechanical

`.gitignore` is an **allowlist** for `inventory/`, `wiki/stacks/`, `wiki/local/`
and `repos.txt`; the root is a blocklist, so check before adding a file there.
Run `bin/leakcheck.py` before every commit — `.leakpatterns` is itself gitignored,
so a fresh clone has no guard until the user writes one. Rationale for both lives
next to the code, in `.gitignore` and `bin/leakcheck.py`.

## `BLOCKED` is not a soft `PASS`

`bin/gate.py` returns **BLOCKED** when the scanner examined nothing — no MCP
servers or skills found. That is an unknown, not a clean bill of health. It
already shipped once as a PASS, which is the most dangerous bug this repo has
had. Treat BLOCKED as "no verdict"; never let it advance an adoption.

## `bin/lint.py` only sees tracked files

A clean lint on an uncommitted page means nothing was checked. Stage first, then
lint, or a new page's broken wikilinks pass silently.

## `bin/pages.py` preserves hand-written notes

Content below the `MARK` line in `wiki/tools/*.md` survives regeneration,
including under `--force`. Anything above it is generated from `ledger.md` and
will be overwritten — put prose below the mark.

## Editing the logo

`assets/logo.svg` is the source; `assets/braintool-banner.png` is what the README
points at, because GitHub renders SVG with the *viewer's* fonts and the wordmark
face is macOS-only.

```bash
rsvg-convert -w 1920 assets/logo.svg -o assets/braintool-banner.png
```

If the mark visibly changes, **rename the PNG**. GitHub's image proxy caches by
URL, so a same-path overwrite keeps serving the old file and the change looks
like it never landed.

## Commands

```bash
bin/weekly.sh      # hygiene: reconcile → churn → pages → lint
bin/discover.sh    # sweep starred repos for candidates
python3 bin/gate.py <target>     # security gate before any adoption
python3 bin/leakcheck.py         # pre-commit privacy guard
```

`bin/*.py` are plain stdlib Python 3.10+. No dependencies, and it stays that way.

## Evidence, not opinion

The `evidence` column takes a number or a path. "Feels slow" is not evidence;
"0 invocations across 2,462 sessions" is. A removal is worth more than an
adoption — write the removals down first.
