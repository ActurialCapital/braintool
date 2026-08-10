---
name: tool-review
description: The weekly tooling review. Read a shortlist of real sessions, judge what was actually happening in them, then propose at most three improvements nobody asked for — a trial, a removal, a rescope, a rule, or an adoption — each with what you saw, where you saw it, and how sure you are. Use when the user says "weekly review", "tooling review", "what should I improve", "anything worth changing in my setup", or after ./bin/weekly.sh finishes. For a question about one named tool, use tool-decisions instead.
---

# Weekly tooling review

`tool-decisions` answers a question the user asked. This is the other direction:
nobody asked, and the job is to surface what they would never think to look for
— including tools they already own and have never once used.

**Brain:** `~/GitHub/ActurialCapital/braintool`

## The counts are not the answer. The sessions are.

`demand.py` cannot see a situation. It counts words and commands, so twenty
turns of one problem look like twenty problems, `--options` looks like
brainstorming, and the strongest signal there is — the user gave up and did it
by hand — leaves no trace it can match.

Its output is a **shortlist of sessions worth reading**, ranked by rework, loops,
failures, and whether any skill fired. Reading those sessions is the review. If
you only summarise the tables, you have done nothing an agent was needed for.

```bash
BRAIN=~/GitHub/ActurialCapital/braintool
python3 $BRAIN/bin/demand.py --days 30 --sample 20   # ~35s, writes the shortlist
cat $BRAIN/inventory/demand.md
```

**Read at least 10 of the shortlisted sessions in full.** Include two you expect
to be boring — a sample of only the dramatic ones will find drama everywhere.

### Start from the session log

`inventory/sessions.jsonl` is written by the `SessionEnd` hook — one line per
session, recorded as it closed: turns, loops, rework, failures, and which skills
fired. It covers every session and costs nothing, so read it before the
shortlist. Sessions where `skills` is empty are the awareness gap in raw form.

```bash
python3 - <<'PY'
import json, collections
rows = [json.loads(l) for l in open("inventory/sessions.jsonl")]
print(len(rows), "logged;", sum(1 for r in rows if not r["skills"]), "fired no skill")
print(collections.Counter(s for r in rows for s in r["skills"]).most_common(10))
PY
```

### Optional enrichment: claude-mem

If `~/.claude-mem/claude-mem.db` exists, it is a plain SQLite file — read it
**read-only**, with stdlib `sqlite3`, and treat it as three different things:

| Table | Trust |
|---|---|
| `user_prompts` | **Verbatim.** Your words, cleanly separated from tool output. Better than any regex over transcripts. |
| `session_summaries` | **Pointers.** `request` / `completed` / `next_steps`, written while the context was warm. Says which session to open; never itself the finding. |
| `observations` | **Not evidence.** Another model's interpretation. Using it means inheriting a judgement without seeing what produced it. |

```bash
python3 - <<'PY'
import sqlite3
c = sqlite3.connect("file:"+__import__("os").path.expanduser(
    "~/.claude-mem/claude-mem.db")+"?mode=ro&immutable=1", uri=True)
for r in c.execute("""select created_at, project, request, next_steps
                      from session_summaries order by rowid desc limit 15"""):
    print(r)
PY
```

**It covered 951 of 2,396 sessions when last checked — roughly 40%.** Never
conclude anything from its silence, and re-check the ratio rather than trusting
that number. If the file is missing, skip this step; nothing downstream depends
on it.

Then, and only then:

```bash
cat $BRAIN/inventory/inventory.md   # what is installed, and what can be observed
cat $BRAIN/ledger.md                # every decision already taken, and every no
```

The ledger goes last on purpose. Read it first and you will only re-find what is
already written down.

## What you are reading for

Five things, none of which any counter can see:

- **The same request, asked three ways.** One situation, not three. The re-asks
  are where the first answer missed.
- **A correction.** "No, don't do that" is a *rule* candidate, not a tool
  candidate — and rules cost a few lines instead of context in every session.
- **The user finishing it by hand** after the agent stalled. The strongest gap
  signal that exists, and completely invisible to keywords.
- **A session that just stops**, unresolved.
- **A skill they own that would have fitted, and nobody mentioned.** This is the
  awareness gap, and reading is the only way to find it.

## Never judge inside a blind window

- **14 days after an install**, zero invocations means nothing. `reconcile.py`
  already marks these "new (grace period)" — believe it.
- **14 days after a removal**, no pain means nothing either. Nobody misses a tool
  in three days. There is no automatic guard for this one; you are it.
- **An untried alternative blocks the decision in both directions.** You cannot
  call a capability missing while a substitute for it sits installed and unused,
  and you cannot bin the substitute before it has been tried once.

## Zero use has four causes. Only one justifies removal.

1. **No demand** — nothing needs doing here. Remove it.
2. **The model never triggered it** — the demand was in the session and the skill
   did not fire. That is a description problem, not a value problem.
3. **The user never knew it was there** — installed months ago, never mentioned
   since. Unmeasurable, and the fix is telling them, not counting.
4. **They knew, but never learned when it is worth reaching for.**

Treating all four as the first is how a good tool gets deleted for a bad reason.

**So: no removal on zero use until the thing has had one deliberate trial.** The
proposal is *"you own this, you have never used it, here is what it does in one
sentence, try it this week."* Only a tool that was actually tried and still did
not earn its place gets a removal row.

Two exceptions that need no trial: a tool whose project no longer exists, and a
tool **superseded** by something more specific that now wins its trigger. Record
supersession as its own reason — it is more useful to the next reader than
"unused".

## Propose at most three

Three is a ceiling, not a quota. A week with nothing worth changing is a real
answer: say so and stop, and write no row for it.

Weigh all five kinds, in roughly this order:

| Kind | Costs |
|---|---|
| **Trial** — use something already installed | one session |
| **Remove** — 0 uses, tried, or its project is gone | nothing; pure win |
| **Rescope** — stack-specific tool at global scope | one move |
| **Write a rule** — a correction they keep repeating | a few lines, no files |
| **Adopt** — install something new | context in every session, forever |

A removal is worth more than an adoption. Look for them first. Adoption is last
because it is the only one that bills you forever, and it runs
`python3 bin/gate.py <target> --stack <type>` first — where **BLOCKED is not a
soft PASS**, it means the scanner examined nothing.

## Every proposal carries its evidence and its confidence

Judgement is not opinion when it can be checked. So each one states:

- **What you saw** — the behaviour, in plain words.
- **Where** — session paths from the shortlist. Quote the opening line.
- **How many** — "in 6 of the 12 sessions I read", not "often".
- **Confidence: high / medium / low**, and what would change it.

The ledger's rule that evidence is a number or a path still holds. A citation and
a count satisfy it; "feels clunky" does not.

## Argue yourself down before showing anything

You are marking your own homework: you will miss what you did not notice at the
time, and you are biased toward proposing tools because proposing something is
more interesting than proposing nothing.

So for each candidate, first make the case *against* it — the demand is normal
work, the window is too short, the tool was never observable anyway. Anything
that does not survive that does not get shown.

## Then write it down, and grade yourself

Accepted or rejected, each proposal becomes a row under a new dated heading, with
its confidence recorded. Never edit a past row — supersede it.

Before proposing, check the ledger for the same idea: **already rejected** means
stay quiet unless the evidence changed, and then lead with what changed.
**Already flagged** means close it — a row still flagged weeks later is the
review failing, not the tool.

Each week, read back your own past rows and report the hit rate: of the
high-confidence proposals, how many were accepted? That number is the point.
Low hit rate means the bar is too low, and saying so out loud is what keeps this
worth reading.
