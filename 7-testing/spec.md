# Testing the solution you built

Your solution is not finished when a claim reaches the end. It is finished when **the right claims stop in the
right places for the right reasons**, and the claimant is told something true.

This document says what to test and what counts as a pass. The commands are in
`7-testing/cookbook.md`.

## The idea

Claims are not real. A **generator** produces them, and it can be *aimed*: you tell it which problem to plant in
the documents, and it writes down what it planted and which analysis has to catch it. So a test is not "run a
claim and read the output" — it is:

```
aim a claim at a known problem  →  let the solution run  →  assert it was caught, by the right analysis,
                                                            at the right point, and said so to the claimant
```

Every claim carries a **manifest** stating what was planted and what must happen. That manifest is the answer
key. Nothing in your solution reads it — no agent, no case, no app. It exists so this test can be mechanical
instead of a matter of opinion.

## What to aim a run at

Two settings control it. Leave them alone and you get a realistic mix; set them and you get a specific claim.

| Setting | Values |
|---|---|
| **Scenario** | `random` (default) · `auto-settle` · `eligibility-fail` · `review-fail` · `both-fail` |
| **Discrepancy** | one exact problem id, or empty to pick one at random within the scenario |

`random` draws roughly **30% clean · 30% a screening problem · 30% a review problem · 10% both**. At most one
problem per category, ever — a claim with three screening failures teaches nothing that one does not.

Pin the exact discrepancy when you are testing. Without a pin, "did it catch the address mismatch?" is a
one-in-five dice roll, and a green run proves nothing about the other four.

## The nine problems, and who has to catch each

The business meaning of each is in `pdd.md` §9 — that is the version to read if you are deciding what
your analyses should look for. This table is the test matrix: the id to aim at, and the check that must be
failing afterwards.

### Screening — visible from the claim form and the policy alone

| Aim at | Must be caught by | Must be failing |
|---|---|---|
| `ELIG_LATE_FILING` | eligibility | filing deadline |
| `ELIG_POLICY_LAPSED` | eligibility | policy status |
| `ELIG_IDENTITY_MISMATCH` | eligibility | identity match |
| `ELIG_ADDRESS_MISMATCH` | eligibility | address match |
| `ELIG_COVERAGE_PERIOD` | eligibility | coverage period |

### Review — needs the assessor's report, or the claim history

| Aim at | Must be caught by | Must be failing |
|---|---|---|
| `REVIEW_AMOUNT_INFLATION` | payout | reasonableness |
| `REVIEW_CAUSE_MISMATCH` | coverage | peril classification |
| `REVIEW_NARRATIVE_CONTRADICTION` | credibility | narrative consistency |
| `REVIEW_PRIOR_CLAIM_EROSION` | payout | aggregate limit |

**Names are yours to choose.** If your eligibility analysis calls its filing check something else, that is fine —
what must hold is that *one* check, owned by *that* analysis, is failing, and that its wording names the actual
problem. A test that only passes when your labels match ours is testing the labels.

## The four assertions

Per claim, in this order. The third is the one that catches the defects the first two miss; the fourth catches
the one that never announces itself at all.

> **Run this block after block 6, not before.** Both gateways are app tasks, so on a case plan built at block 5
> they do not exist: nothing stops at screening, no Action Center task is ever raised, and a claim carrying a
> planted problem runs past its gateway and closes approved. A build measured before the app exists therefore
> fails **eight of the nine pinned runs** and the table it produces says nothing about the solution — it says the
> app is missing, which you already knew. Measured 2026-08-20; one build spent a full pass discovering it.
>
> What *is* worth running at block 5 is the clean claim, alone, which is that block's own acceptance gate.

**1. It stopped where it should.** Every claim reaches the **screening gateway** — that one is never skipped, not
even for a clean claim. A claim carrying anything flagged must *also* reach the **adjuster gateway**. A clean
claim must not: it settles unattended after screening is approved, and an adjuster task appearing for it is a
failure even though nothing looks wrong on screen.

**2. The right analysis is failing the right check.** Not "something was flagged" — the analysis that *owns* the
concern must be the one reporting it. Three analyses all reporting the same late notice is not three findings; it
is one finding and two scope violations, and it makes the reviewer's screen unreadable.

**3. The letter says it.** The manifest states what the claimant's letter has to mention. Check the letter text,
not the decision field.

> Assertion 3 exists because assertions 1 and 2 have both passed while the letter said something else entirely.
> A claim was approved, recorded as approved, and mailed a letter saying it "remains under specialist review",
> asking the claimant to itemise their cash and documents — under the subject line *"Your claim has been
> approved"*. Every field was right. Only the sentence the human reads was wrong.

**4. Nothing was truncated.** Every JSON column on the claim record is capped at 10,000 characters and the
write **succeeds** when the payload is longer — it simply arrives cut. So the only symptom is the length itself:

```bash
uip df records get <entity-id> <record-id> --output json    # then check the length of every *Json field
```

Any field whose length is exactly 10,000 has been truncated. Treat it as a failed run, not a near miss: the loss
lands in whichever payload was richest, which is the claim with the most damage rows — the interesting one.

> This assertion is temporary. It exists because the field type that would hold 128 KB is in private preview;
> when it arrives, the cap and this check go together. Until then it is the only thing standing between a
> silently halved policy document and a reviewer making a decision on it.

## What a clean claim proves

Run the clean scenario deliberately, and more than once. It is the assertion most solutions fail:

- every check passes, and the analyses say so rather than staying silent;
- the adjuster gateway never appears;
- the claim settles at the full amount the policy allows;
- the letter states the amount and how it was reached.

**A solution that finds something to flag on every claim has not passed.** It has learned to always answer *yes*
to "is anything wrong here?", which is the easiest way to look thorough and the least useful.

**This is also block 5's acceptance run**, and the reason it comes first: a clean claim is the only claim that
can run the whole plan without a human, so it is the only one that can prove the spine works before the app
exists. Run `auto-settle` as soon as the case deploys.

### When the clean claim gets flagged

The case plan is not what is wrong. It parked the claim at the review stage exactly as it was told to, because
an analysis said something was off with a claim that has nothing off about it. Find which one from the row it
wrote:

```bash
uip df records query <entity-id> --folder-key <your-seat-folder-key> --output json
```

`eligibilityChecksJson`, `coverageChecksJson`, `payoutChecksJson`, `credibilityChecksJson` and
`decisionJson` each name their own checks and say which failed. One of them will be holding a *pass* claim to a
standard the process never asked for — a missing optional field read as an omission, a rounding difference read
as a discrepancy, a silence read as a refusal.

**Fix the agent's prompt, not the case plan and not the entity.** Then republish that one agent and run
`auto-settle` again. Over-flagging is the most common defect in this whole build and the only thing that
reliably exposes it is a claim with nothing wrong.

## How many, and in what order

1. **One per problem, pinned** — nine runs. This is the coverage test, and it is the one to keep green.
2. **At least two clean runs.** See above.
3. **Then twenty on `random`**, unpinned. Assert each against its own manifest. This is where interactions
   surface: two problems in one claim, a currency you had not tried, a claim with four damage items instead of
   five.

Run them concurrently. A claim spends most of its life waiting.

## Recording the result

For each run keep the claim id, what was aimed at, the three assertions, and — when one fails — the actual text
the analysis produced. **The text matters more than the pass/fail.** An analysis that fails the right check for
the wrong reason will pass this test and mislead a reviewer on a real claim; the wording is the only place that
shows.

Keep the failures. A test pass that records only successes cannot tell you whether your solution got better.
