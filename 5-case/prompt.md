# Block 5 — the claim's journey

**Goal.** Make a claim actually move. Everything built so far is a component sitting on its own; this is the
thing that runs a claim from the moment it arrives to the moment it closes.

**Read.** `2-design/` (your own design — the journey you mapped out) · `5-case/spec.md` (the design decisions
this has to honour) · `contracts/provided-processes.md` (the automations already running that you connect to) ·
`contracts/claim-entity.md` (what gets recorded, and when) · `contracts/review-task.md` (what a claim hands a
person at the two stops, and what they hand back) · `5-case/cookbook.md` (how to build it here — read the first
two sections before you edit anything)

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

## The two people are part of the journey, even though their screen is not built

The eligibility reviewer and the claims adjuster each need a screen and that is the next block. **What belongs
here is the stop itself** — where the claim waits, what the person is asked, and what their answer does to the
rest of the journey.

So you build both stops now, working, with a **stand-in** where the screen will go: something a person can
actually open and complete, with nothing on it. A door frame before the door. The frame's dimensions are what
everything else gets built around, and `contracts/review-task.md` fixes them — what the claim hands the reviewer
and what they hand back. That shape is settled and is not yours to design.

**This is the cheaper order and it is not close.** Those dimensions are what the journey binds to, so changing
them later means unpicking the wiring at both stops. Build the frame now and the journey is done when this block
is; leave it and the next block spends most of itself back in here.

## Do it in four passes

This is the longest block. Finish each pass before starting the next, so a pass that goes wrong costs a pass
rather than the block — and **write down where you are between them**, in the notes this block ends with. You
will lose your working context partway through, and that note is what makes the next hour cheap.

1. **The journey.** Every stage, how a claim enters it, what ends it. No work in them yet.
2. **The stand-in, first.** Publish the blank screen and register it, before anything binds to it. A task that
   stops a claim for a person is described in terms of the app's identity and its two answers, so pass 3 cannot
   be written until this exists. Doing it here also makes passes 2 and 3 one continuous edit.
3. **The work, the wiring and the two stops.** What happens in each stage, connected to the components you have
   built and the automations already running, with the record written as the claim moves — and what each answer
   at each stop does, including the endings it leads to.
4. **Run claims through it** — the clean one, and one into each answer at each stop.

## Done when

**Every route through the journey has carried a real claim.** Three things, and the first is the one people stop
at:

- **A straightforward claim goes in one end and comes out settled, with nobody touching it — and it raises no
  task at all.** Nothing wrong with it, nothing to query: read, screened, inspected, analysed, approved, the
  claimant told, the file closed, with its record showing each stage's work as that stage did it. If a screen is
  waiting for a person on a claim with nothing wrong, that is the failure, not the proof.
- **A claim stops at each of the two stops**, waits, and moves on when a person answers.
- **Both answers work, at both stops.** Agree and it carries on; disagree and it ends the other way, with the
  claimant told the right thing. That is **four aimed runs plus the clean one — five**, and the four are the ones
  that find the bugs: every route a claim can take now exists, so every one of them can be wrong.

You answer the stops by hand, on a blank stand-in — **you are proving the journey, not the screen.** Get all four
routes right now and the next block cannot break them; it only changes what the person is looking at.

**And the journey is written down**, in `5-case/notes.md`: the stages and how a claim moves between them, what
happens at each stop, the identifiers the next block will reach for constantly (your seat's folder key, the claim
entity's id, the aimed run that stops a claim at each gateway), what you had to work out that the instructions
did not tell you, and anything left deliberately unfinished. Not a diary — the briefing you would give someone taking over, because **block 6 is the
person taking over**, usually with none of this in mind. Reading it costs five minutes; reconstructing it from
the plan file costs an hour.

**And you have read the letter.** Every route ends by writing correspondence to the claimant, and it is the
second of the only two things a human ever sees. Open the one written on the denial route and read it as the
claimant would: it must be in English, say why in plain words, and contain no internal codes, no stage names and
no placeholder. **An analysis that could not do its job must say so where the process can see it — never in the
letter.** One build produced a fluent letter whose entire content was the agent explaining it lacked the inputs
to write one; every structural gate passed.

**And you have read the cookbook back** — the two-sided review in `AGENTS.md`, *Before you finish a
block*. Two minutes, and it is what keeps this seed from only ever growing.

## How to test it

`5-case/cookbook.md` has the exact calls, including how to answer a stop without a screen. Deploying and running
are **pre-authorised** (`AGENTS.md`): your seat, synthetic claimants, no letter ever sent. Do not stop to ask, and
do not end this block before the runs — a plan that has not carried a claim proves nothing.

**Read the claim's record, not the journey's status.** A claim can reach an ending with a stage that never ran,
and the record is the only place that shows it: a stage that went green and left its columns empty did not do its
job, whatever the status says.

**If the clean claim gets stopped for review, the journey is not what is wrong.** It parked exactly where it was
told to, because one of your analyses found fault with a claim that has none. That is a block 4 fix.

**Where it goes.** Generated code into `Build/ClaimCase-<seat>/` — one solution for the whole build, holding the
journey and all seven analyses. Notes and documents you write for this block go in this block's folder, and
`5-case/notes.md` is the one this block is not finished without.

**Log as you go.** `python3 log-finding.py --block 5-case --category <kind> --summary "..."` — every retry,
every surprise, everything these instructions failed to explain, and anything that took longer than it should
have. Dead ends included; they are the point. `AGENTS.md` has the detail.
