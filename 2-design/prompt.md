# Block 2 — the design

**Goal.** Work out how this claims process becomes a solution, and write it down — so that the six blocks after
this one are assembly rather than invention. Nothing is created on the platform here.

**Read.** `pdd.md` — all of it, once, before writing anything · `contracts/` (the shapes that have to match
across components) · `2-design/spec.md` (what your design has to answer) · `2-design/cookbook.md` (how to
produce it here)

## What the business is asking for

A claims manager has described how property claims are handled: what arrives, what gets checked, where a person
has to decide, and what the claimant is told. That description is `pdd.md`. It says what must happen and
deliberately does not say which piece of software does it — that is the design work, and it is yours.

You are being asked for the document a solution architect produces before a team starts building: **what the
solution is made of, how a claim moves through it, what data passes between the parts, and who is accountable for
catching each thing that can go wrong.**

## What the design has to settle

- **The claim's journey, end to end** — every stage a claim can be in, how it gets there, and what ends it.
  Including the unhappy paths and the endings. A branch left out here becomes a gap in the built solution.
- **Every piece of data, traced from where it is produced to where it is read.** What produces it, what it is
  called while the claim is in flight, where it is stored, and who consumes it. This is the single most valuable
  table you will write, and the one whose absence costs most.
- **Who catches what.** The process description lists nine things that go wrong with real claims. Each needs
  exactly one owner: which check finds it, what that check reports, and where a human would see it. Deciding the
  owner is the work — the list is given.
- **Where the two people sit** — which point in the journey each human decision belongs at, what that person is
  shown, and what the process does with their answer.
- **What happens at the same time.** Independent checks written as a sequence get built as a sequence, and the
  claim takes four times as long for no reason.
- **The name of every check, as a closed list per analysis.** This is the only point in the exercise where all
  seven analyses are in front of you at once; the block that builds them writes seven prompts separately and has
  every reason to invent a neighbouring name in each. Nine of the names are already fixed by the process
  description — take those verbatim — and settle the rest here, in one sitting, rather than discovering in
  block 7 that two analyses report the same concern under two spellings.

## Done when

You can answer these three from your own document, without going back to the process description:

1. Pick any one of the nine problems: which check catches it, what does it report, and where does a human see it?
2. Pick any stored field: what produces it, and at which stage?
3. Pick any stage: what has to be true for a claim to enter it, and what ends it?

If any answer sends you back to `pdd.md`, the design is not finished — and the cost of that lands in block 5,
not here.

**Log as you go.** Every retry, every surprise, everything these instructions failed to explain, and
anything that took longer than it should have — dead ends included, they are the point. `AGENTS.md`
says how, and closing the block includes the two-sided read-back of what you were handed.

