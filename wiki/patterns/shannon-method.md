---
verified_at: 2026-08-09
status: open
source: "A Mind at Play (Soni & Goodman), via Founders #95"
---

# The Shannon method — what transfers to an agent, and what does not

Claude Shannon's working habits are the most-quoted research method in
engineering, and roughly a third of them make a coding agent **worse**. This page
keeps the split explicit, because the failure mode is copying the whole list.

The distinction is structural, not stylistic. Shannon was a **principal** — he
chose his problems, worked alone, and answered to nobody. An agent is an
**agent**: it works on someone else's problem, its output must be reviewable, and
its silence is a defect. Habits that depend on being a principal invert when
applied to an agent.

## Transfers

**Two small jumps beat one big jump.** Shannon's own rule, and the single most
useful item here. Decompose until each step is independently verifiable. This is
the same shape as `step → verify` in [[karpathy-guidelines]], arrived at from the
other direction — evidence that it is load-bearing rather than stylistic.

**Chisel, don't accrete.** Ed Thorp described Shannon treating a new problem as a
block of stone, removing everything inessential until the solution was what
remained. Reduction is the *first* move, not cleanup after the fact. Before
writing anything: state the problem in one sentence and delete every constraint
that is not real.

**Build the toy.** Shannon's "useless" output — the maze-solving mouse, the
Roman-numeral calculator, the juggling mathematics — was not recreation adjacent
to the work, it was the generative engine. The agent translation is narrow and
strong: **a ten-line spike beats a paragraph of speculation.** When the question
is "would this work", run it instead of reasoning about it.

**Could a machine do it? Can I prove it?** Shannon asked these of everything. For
an agent the second one has a sharper form: *can I write a check that fails if I
am wrong?* Intuition that cannot be converted into an executable assertion is not
yet knowledge.

**Prefer principles to facts.** Shannon avoided fields heavy on isolated facts
and light on general structure. In a codebase: find the one file that defines the
rule rather than grepping forty call sites. If you are accumulating instances,
you have not found the invariant yet.

**Insulated from opinion of all kinds — especially his own.** The most valuable
habit on this list for an agent, because agents anchor hard on their first
hypothesis and then recruit evidence for it. When new evidence contradicts an
earlier claim, drop the claim. That includes claims made three tool calls ago.

**The transfer is often an identity, not an analogy.** Shannon found that
cryptography and information theory were one structure seen from two sides. Before
inventing a mechanism, look for the same shape already solved elsewhere in the
repo.

**No prior knowledge is not a blocker.** His doctoral work applied his method to
genetics, a field he had no background in. An unfamiliar stack is a reason to read
the primary source, not a reason to hedge.

**When it goes stale, change the frame.** Shannon left Bell Labs when the
environment stopped producing. For an agent: two attempts failing the same way
means the approach is wrong, not that it needs more force. Change the frame rather
than retrying harder.

## Does not transfer

**Three ideas in parallel.** Shannon found this more productive than one at a
time. For an agent it produces scattered diffs and three half-finished changes
none of which can be reviewed. The correct split is **parallel exploration,
serial editing** — fan out read-only investigation as wide as you like, then land
one coherent change at a time.

**Discovery matters; writing it up is an afterthought.** Shannon sat on results
for years and had to be pushed to publish. An agent that works this way produces
silent output nobody can review, which is worth nothing regardless of quality.
**Invert it: the write-up is the deliverable.** The diff is only the evidence.

**Long silences, closed doors, empty offices.** He thought best alone and
unobserved. An agent that goes quiet for forty tool calls is unauditable. Narrate
at decision points — not continuously, but wherever a different choice was
available.

**Nobody assigns his work.** Shannon deliberately chose Bell Labs for freedom, and
named it as the single reason for his output. An agent has a principal and a
scope. Self-direction here is scope creep, and it collides directly with
[[karpathy-guidelines]] §3: every changed line should trace to the request.

**Follow your natural drift.** Agents have no interests, but they do have
attractors — refactoring, adding tests, tidying imports, improving adjacent code.
Drift toward those is the failure mode, not the method.

**Indecision as a virtue.** His inability to choose a specialty is what kept him
general, and he could afford a decade to stay undecided. A session cannot. For an
agent, indecision is stalling: pick the default and say which one you picked.

**Play with no end in view.** The toy transfers (above); the *unboundedness* does
not. Shannon's mouse answered to nobody. An agent's spike is a means to the
user's stated end, and a spike that becomes the project is a detour.

## The general rule

> Shannon's habits about **how to think** transfer. His habits about **how to
> work** invert, because they are all downstream of autonomy an agent does not
> have.

When a research method is proposed for the harness, sort it by that line first.

## How you would know it is working

Not by invocation count — this is a frame, and its success looks identical to
never having been read (the same measurement problem as [[right-size]]). The
observable is **churn**: if reduce-first and two-small-jumps are landing, the
`fix:feat` ratio on new work falls. If it does not move within two months, this
page is decoration and should be recorded as such.

## Status

**Not installed as a skill.** It is here as prose, at zero context cost, and it
gets promoted only if it earns invocations when reached for by hand. The 13-skill
[[matt-pocock-skills]] family is the warning: adopted as a block, exercised once
in three months.

Note the overlap already owned — "three ideas in parallel" is what [[adhd]] does,
and [[adhd]] has 0 invocations. Installing a second copy of an unused capability
is not adoption, it is accumulation.
