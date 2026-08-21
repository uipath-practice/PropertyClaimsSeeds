# Block 3 — the claim record

**Goal.** Every claim needs one place where everything known about it lives. Create it.

**Read.** `contracts/claim-entity.md` (the agreed schema — all of it) · `pdd.md` §8 (why the record exists) ·
`3-claim-record/cookbook.md` (how to create it here, and what breaks)

## What the business is asking for

A claim passes through eight stages, six automated steps and up to seven analyses, and two people make decisions
about it. Each of those produces something someone later needs: what was extracted, what each check concluded,
what the settlement came to, who approved it and why.

**Without somewhere to put that, none of it survives the step that produced it.** The reviewer's screen has
nothing to show, an operations view has nothing to count, and nobody can answer what happened to a claim last
Tuesday. So: one record per claim, written to as the claim moves, holding all of it.

## The schema is already agreed

`contracts/claim-entity.md` fixes every column, its type, and the limits that matter. This is not a design
exercise — the shape was settled with the people who consume it, and three later components are already written
against it. Nothing here is inferred and there is nothing to arbitrate.

**If your tooling asks you to confirm a schema before creating it, treat that contract as the confirmation** and
proceed. The approval it is waiting for has already been given.

Two things about the shape are worth understanding rather than copying, because they shape what you build later:

- **The reasoning is stored, not just the conclusions.** Each analysis writes what it found and why, in full,
  rather than a verdict. That is what makes a reviewer's screen possible and an audit answerable.
- **A handful of facts are their own columns rather than part of a blob** — the claimant, the amount, the
  incident type, the dates. Those are what an operations view filters and sorts on, and something buried inside a
  blob can be neither.

## Done when

The record exists, and everything your design says a claim accumulates has somewhere to go. Read your own data
table from block 2 against it: a payload with no home is a gap you will otherwise discover at run time in block
5, when a write fails against a column nobody created.

## One thing you will need later, so find it now

The record is written by the case, and the case reaches it through a connection that **already exists and is
shared across the team**. Confirm you can see it and that it answers, and note what it is called — block 5 binds
to it. Do not create your own: authorising a connection needs a human at a browser, and one each buys nothing.

**Where it goes.** Generated code into `Build/ClaimCase-<seat>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** `python3 log-finding.py --block <this-block> --category <kind> --summary "..."` — every
retry, every surprise, everything these instructions failed to explain, and anything that took longer than it
should have. Dead ends included; they are the point. `AGENTS.md` has the detail.
