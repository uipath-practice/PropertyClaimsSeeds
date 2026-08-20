# Block 2 — the design

**Goal.** Turn the process description into the four tables the rest of the build is assembled from, and an SDD
that explains the solution to a person. Nothing is created on the platform in this block.

**Read.** `pdd.md` — all of it, once, before writing anything · `contracts/` (the shapes that must match across
components) · `2-design/spec.md` (what the tables must contain, and how the `uipath-planner` skill fits) ·
`CONFIG.md`

**Why this block exists.** Everything after it is assembly, and assembly against a table you wrote is an order
of magnitude cheaper than assembly against a document you re-read each time. Blocks 4 and 5 in particular are
long enough that you will lose your working context partway through; when you do, these tables are what you come
back to instead of `pdd.md`.

**Must hold.**

- **Every stage in the lifecycle appears, with how a claim enters it and what ends it** — including the stages
  a claim reaches only when something is wrong, and the endings. A branch you leave off here becomes a dead box
  on the canvas in block 5.
- **Every payload is named once and traced end to end** — which component produces it, what it is called as a
  case variable, which entity column stores it, and who reads it. One name in three casings
  (`contracts/claim-entity.md`); the mapping breaks silently three blocks later if you improve a name.
- **Each of the nine planted problems has exactly one owner** — the analysis that must catch it, the field that
  carries the finding, and the stage where a human would see it. `pdd.md` §9 lists the problems; deciding who
  owns each is the work.
- **The two human decisions are placed** — which stage each sits in, what it shows the reviewer, and what the
  case does with the answer.
- **What runs in parallel is marked as parallel.** Independent analyses that you list in sequence will be built
  in sequence, and the claim will take four times as long for no reason.

**Done when.** You can answer these three from your own tables, without going back to `pdd.md`:

1. Pick any planted problem: which analysis catches it, which field carries the finding, which stage shows it?
2. Pick any entity column: which component writes it, and at which stage?
3. Pick any stage: what has to be true for a claim to enter it, and what ends it?

If any answer requires re-reading the process description, the tables are not finished — and the cost of that
lands in block 5, not here.

**Where it goes.** `2-design/` — the tables and the SDD, as markdown. This block writes no code, so nothing
goes in `Build/`.

**Log as you go.** `python3 log-finding.py --block 2-design --category <kind> --summary "..."` — every retry,
every surprise, everything these instructions failed to explain, and anything that took longer than it should
have. Dead ends included; they are the point. `AGENTS.md` has the detail.
