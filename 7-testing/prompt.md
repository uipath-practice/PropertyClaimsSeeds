# Block 7 — does it actually work?

**Goal.** You have built a claims process. Now find out whether it would survive contact with real claims —
before someone else does.

**Read.** `pdd.md` §9 (the nine things that go wrong with real property claims) · `2-design/` (your own
traceability table — which of your checks you made responsible for each) · `7-testing/spec.md` (what counts as a
pass, and why) · `7-testing/cookbook.md` (how to run it here)

**Before you start:** the reviewer's screen from block 6 has to be built and working. Most of these claims are
supposed to stop and wait for a person, and without somewhere for that person to decide, they will sail past and
close — which looks like your analyses failing when it is only the screen missing.

## What the business is asking for

A claims manager is not going to sign this off because it ran. They are going to ask: *"what happens when
somebody claims for a leak they have been ignoring for two years?"* — and expect you to know.

`pdd.md` §9 lists nine such things: a policy that had lapsed, an address that does not match, an inflated
estimate, a story that does not hold together, a prior claim that has eaten most of the annual limit. Every one
of them happens, and each has a right answer — sometimes reject, sometimes reduce and flag, sometimes pause and
ask a human.

**You are being asked to demonstrate, one claim at a time, that your solution gets each of them right.**

## What a pass actually means

It is not "the claim stopped". Four things have to be true together, and the third is the one that separates a
working solution from a lucky one:

- **It stopped in the right place** — at the screening gateway or the adjuster's, whichever the problem calls
  for. A claim caught too late has already had a surveyor sent out for nothing.
- **The right check caught it.** If the coverage analysis flags something the credibility analysis owns, the
  outcome is right and the solution is wrong: on the next claim the same mistake produces the wrong answer, and
  nobody will know why.
- **A reviewer could act on what it says.** The finding has to name the actual problem — *"the policy lapsed
  eleven days before the incident"* — not the rule that fired.
- **The claimant was told something true.** The letter has to match what was decided. A claim approved and a
  letter saying it remains under review is a complete failure that every other check passes.

And the one that catches most solutions:

- **A claim with nothing wrong with it must go through untouched.** Run more than one. A solution that finds
  something to query on every claim has not learned to be thorough, it has learned to always say yes — and it
  costs a claims team more time than it saves.

## Done when

You can show a claims manager one table: nine known problems, what your solution did with each, whether that was
right, plus clean claims that went through unattended.

**Keep the failures in it.** A results table with only successes cannot show anyone that the solution improved,
and it is the failures that tell you what to fix.

**And you have read the cookbook back** — the two-sided review in `AGENTS.md`, *Before you finish a
block*. Two minutes, and it is what keeps this seed from only ever growing.

## How to test it

Every run is **aimed** — you decide which problem the claim carries before you send it in, so you know what
should happen. An unaimed run that goes green tells you one claim passed, not that a check works.
`7-testing/cookbook.md` has the exact call.

Judge each run against what was actually planted rather than against what looks reasonable. The generator writes
down what it put in every claim and what should happen to it — **this is the one block allowed to read that**,
because here it is the answer key rather than a shortcut.

Then, once the nine behave, send in twenty unaimed claims and see what a normal week looks like.

**Where it goes.** The results table in this block's folder. Generated code, as ever, in `Build/ClaimCase-<seat>/`.

**Log as you go.** `python3 log-finding.py --block 7-testing --category <kind> --summary "..."` — every retry,
every surprise, everything these instructions failed to explain, and anything that took longer than it should
have. Dead ends included; they are the point. `AGENTS.md` has the detail.
