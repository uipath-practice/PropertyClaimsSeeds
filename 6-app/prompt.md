# Block 6 — the reviewer's screen

**Goal.** Two people have to sign off on a claim, and neither of them has anywhere to do it yet. Build the screen
they use.

**Read.** `pdd.md` §2 and §6 (who these two people are, and what their approval binds) · `2-design/` (your own
tables — what each analysis produces and which column it lands in) · `5-case/` (your own notes — the two stages
you shaped and left waiting, and what you wrote down for this block) · `6-app/spec.md` (the design decisions
already taken) · `6-app/cookbook.md` (how to build it here, and what has cost other people time)

You may be starting this block in a fresh session, with none of block 5 in your head. That is normal and it is
why those notes exist — read them before anything else, because the two stages waiting for this screen were
built with an interim exit that you are about to replace.

## What the business is asking for

Twice in a claim's life the process stops and waits for a person.

The **eligibility reviewer** goes first. A claim has been screened, something about it looks wrong — the policy
may have lapsed, the address may not match, it may have been reported too late — and before anyone sends a
surveyor out to inspect a property, a human decides whether this claim should be pursued at all. They see the
claim, the policy and the screening findings. Nothing else exists yet.

The **claims adjuster** goes second, and only when the analysis recommends it. By then there is a surveyor's
report, a coverage assessment, a settlement calculation and a credibility check, and the recommendation is that
somebody look before this is settled. They see all of it and make the final call.

Both of them are doing the same job — reading what the machine found and deciding whether they agree — so
**build one screen and use it at both points**. At the first gateway most of the analysis has not happened yet;
say so on the screen. A section that is empty because the work has not been done reads as a broken page unless
it tells the reviewer why it is empty.

## What a reviewer has to be able to do

- **Understand the claim without opening anything else.** Who claimed, for what, how much, against which policy,
  and what each analysis concluded — in sentences, not field names. If your screen shows a reviewer
  `recommend_review` or `is_eligible: false`, it is not finished.
- **Read the three documents** — the claim form, the policy, and the surveyor's report where one exists.
- **Disagree with the machine.** Approving and rejecting are equally available at both gateways, and the
  recommendation is a recommendation.
- **Say why, in their own words.** The written reason is not optional and it is not decoration: every analysis
  after the gateway reads it and is bound by it (`pdd.md` §6). A decision with no reason leaves the rest of the
  process guessing at what the human meant.

## Done when

A claim that the process has flagged is waiting for a human, someone can open it, read what was found, decide,
and the claim carries on and reaches an ending — approved or denied — carrying that person's decision and their
words.

Then the same screen, at the other gateway, on a claim that got that far.

## How to test it

Send a claim through the process that you know will be stopped — `6-app/cookbook.md` says which input produces
one, and how to find the waiting task. Then work it the way a reviewer would: read it, decide, and follow the
claim to its ending.

Two things to check that are easy to miss, and both have caught real builds:

- **Reject as well as approve.** A screen wired only for the happy answer looks complete and fails the first time
  a reviewer disagrees.
- **Look at the claim's record afterwards.** The decision, the reason and the time it was made all belong on it.
  A screen that submits successfully and stores nothing looks identical from the front.

**Where it goes.** Generated code into `Build/ClaimCase-<NN>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** `python3 log-finding.py --block <this-block> --category <kind> --summary "..."` — every
retry, every surprise, everything these instructions failed to explain, and anything that took longer than it
should have. Dead ends included; they are the point. `AGENTS.md` has the detail.
