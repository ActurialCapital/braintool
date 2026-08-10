---
verified_at: 2026-08-09
status: rejected
scope: global
---

# karpathy-guidelines

**rejected** as of 2026-08-09, for **global**.

## Decisions

| Date | Scope | Decision | Evidence | Reason |
|---|---|---|---|---|
| 2026-08-09 | global | **open** | 4 sections; 3 already covered by an installed always-on rule set | Only §3 *Surgical Changes* is new — "every changed line traces to the request", don't improve adjacent code. §2 and §4 restate rules already loaded every turn. §1 ("if unclear, stop and ask") **contradicts** the standing rule to act on a sensible default rather than stall. Adopting the block would buy one idea, three duplicates and one conflict. Candidate action: lift §3 into global rules, install nothing. |
| 2026-08-09 | global | **adopted** | 1 of 4 sections lifted; 0 files installed | *Surgical Changes* — every changed line traces to the request, don't improve adjacent code, remove only the orphans your own edit created. Written into global rules in ~6 lines. The other three sections stay out: two duplicate always-on rules already loaded, one was rejected below. Adoption without installation — the idea moved, the package did not. |
| 2026-08-09 | global | **rejected** | 0 installed rules carry ask-first; 2 state the opposite | *Think Before Coding* asks the agent to stop and ask whenever something is unclear. Conflicts with the standing rule to act on a sensible default and state the assumption. Resolved in favour of acting: an agent that stops on every ambiguity converts a 1-turn task into 3 and pushes its own judgement onto the user. Ambiguity gets a stated assumption, not a question. Blocking questions stay reserved for work that would be unsafe or useless if the guess is wrong. Note the failure mode this accepts: occasional confident work in the wrong direction, cheaper to redo than to prevent. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
