# Block 5 — the claim's journey

**Goal.** Make a claim actually move. Everything built so far is a component sitting on its own; this is the
thing that runs a claim from the moment it arrives to the moment it closes.

**Read.** `2-design/` (your own design — the journey you mapped out) · `5-case/spec.md` (the design decisions
this has to honour) · `contracts/provided-processes.md` (the automations already running that you connect to) ·
`contracts/claim-entity.md` (what gets recorded, and when) · `5-case/cookbook.md` (how to build it here — read
the first two sections before you edit anything)

## What the business is asking for

A claim arrives. Over the next hours or days it gets read, screened, inspected, analysed, decided and closed, and
at two points a person has to look at it. Right now none of that is joined up.

You are building the thing that runs it: **the stages a claim passes through, what happens in each, what waits
for the outside world, what can happen at the same time, and where the record gets written.**

Three things about how the business works, which the shape has to reflect:

- **Some of the work already exists and is running.** Generating the claim documents, reading the form,
  fetching the policy, pulling the claim history, chasing the surveyor's report, writing to the claimant — those
  are automations the team already operates. You connect to them; you do not rebuild them. If you find yourself
  writing a document download or a PDF-to-text step, you have missed one (`contracts/provided-processes.md`).
- **A claim waits for the outside world.** A surveyor has to visit the property. The process cannot hurry that
  and must not fail because of it — it holds, and picks up when the report arrives.
- **Independent work happens at the same time.** Coverage, payout and credibility are three people's jobs done
  in parallel in a real claims team, and a claim that queues them takes four times as long for no reason.

## The two people are not in place yet

The eligibility reviewer and the claims adjuster each need a screen, and that is the next block. So the two
stages where they belong get built **now, in their right places, shaped and waiting** — with no task in them yet.

That is deliberate and it is the cheaper order. A stage merged away or made to complete instantly has to be
rebuilt rather than extended, and the wiring around it is the expensive part. `5-case/spec.md` says exactly what
"shaped and waiting" has to mean, because the difference between *correctly waiting* and *broken* is invisible
from the outside.

## Do it in three passes

This is the longest block. Finish each pass before starting the next, so a pass that goes wrong costs a pass
rather than the block — and **write down where you are between them.** You will lose your working context
partway through this; that note is what makes the next hour cheap, and the block after this one begins by
reading it.

1. **The journey.** Every stage, how a claim enters it, what ends it. No work in them yet.
2. **The work, and the wiring.** What happens in each stage, connected to the components you have built and the
   automations already running, with the record written as the claim moves.
3. **Run a claim through it.**

## Done when

**A straightforward claim goes in one end and comes out settled, with nobody touching it.**

Nothing wrong with the claim, nothing for a reviewer to query: it should be read, screened, inspected, analysed,
approved, the claimant told, and the file closed — and its record should show each stage's work as that stage
did it.

That is the whole gate for this block. **Do not run the problem claims yet** — every one of those is supposed to
stop and wait for a person, and there is nobody there until block 6.

## How to test it

Ask for a claim with nothing wrong with it and follow it through. `5-case/cookbook.md` has the exact call.

Then read the claim's record rather than the journey's status. A claim can reach an ending with a stage that
never ran, and the record is the only place that shows it: a stage that went green and left its columns empty did
not do its job, whatever the status says.

**If the clean claim gets stopped for review, the journey is not what is wrong.** It parked exactly where it was
told to, because one of your analyses found fault with a claim that has none. That is a block 4 fix.

**Where it goes.** Generated code into `Build/ClaimCase-<NN>/` — one solution for the whole build, holding the
journey and all seven analyses. Notes and documents you write for this block go in this block's folder.

**Log as you go.** `python3 log-finding.py --block 5-case --category <kind> --summary "..."` — every retry,
every surprise, everything these instructions failed to explain, and anything that took longer than it should
have. Dead ends included; they are the point. `AGENTS.md` has the detail.
