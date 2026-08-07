---
verified_at: 2026-08-07
status: open
---

# Acceptance test: does this brain actually work?

A knowledge base that only records what already happened is a diary. The test is
whether it **surfaces something true that was not obvious at the time**.

## The standing test — superpowers restore

On 2026-08-07 the [[superpowers]] framework was removed. Transcript evidence,
found only after the fact:

- **143 invocations** across 2,539 sessions — the most-used skill family on the machine
- Last used **2026-08-06**, the day before removal
- 138 of 143 came from five skills: `brainstorming` (46), `writing-plans` (31),
  `subagent-driven-development` (29), `systematic-debugging` (19),
  `finishing-a-development-branch` (13)
- Their replacements — [[adhd]], [[design-first]], [[diagnose]] — carry 0, 0 and 1 uses

The five skills were **deliberately not restored by hand.**

> **The brain passes if it recommends restoring those five skills — standalone,
> without the 72-file repo clone — on its own evidence, through the weekly PR.**

If a human has to reach in and restore them, the brain is decoration.

## Why this is a fair test

It requires the loop to do all four jobs at once:

1. **Reconcile** — notice a capability that used to be exercised and now is not
2. **Measure** — connect that gap to an outcome signal (churn, or a fall in
   planning/debugging invocations with no replacement picking up the load)
3. **Separate tool from packaging** — the skills were good; the repo clone was the
   problem. A naive "re-add what was removed" would restore the 200 phantom commands too.
4. **Propose, not act** — arrive as a reviewable PR with the evidence attached

## Second test — the ag-grid hypothesis

the private stack page `ag-grid` scope: **5.00 fix:feat** (9 feat / 45 fix), the worst real
scope in the repo, *while* [[ag-mcp]] is installed and connected.

Two possible truths, and the brain should say which:

- **ag-mcp is never reached for** → prompt/routing problem, not a tool problem
- **ag-mcp is used and churn stays high** → the tool does not help; drop it

Either answer is worth more than the tool itself. An honest "this thing you
installed is not helping" is the hardest output for a recommender to produce,
which is precisely why it is the test.
