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
| `REVIEW_PRIOR_CLAIM_EROSION` | payout | aggregate limit — **and its evidence must name the earlier claim** |

**Names are yours to choose.** If your eligibility analysis calls its filing check something else, that is fine —
what must hold is that *one* check, owned by *that* analysis, is failing, and that its wording names the actual
problem. A test that only passes when your labels match ours is testing the labels.

**The aggregate row has a second half that a build will pass without.** `pdd.md` §9 says *cap the settlement at
what remains **and name the earlier claim***. Measured on a real run: the arithmetic was right to the unit — a
SGD 16,600 claim correctly cut to 9,807 — and the only evidence offered was *"One settled claim in this policy
period"*. No number, no date, no identifier, and none of the three figures a reviewer needs anywhere on the
record. That build passes the first three assertions and asks a human to authorise a 41% reduction blind. Assert
the evidence, not only the reduction.

## The assertions

Per claim, in this order. The third is the one that catches the defects the first two miss; the fourth catches
the one that never announces itself at all.

> **Run this block after block 6, not before.** Both gateways are app tasks, so on a case plan built at block 5
> they do not exist: nothing stops at screening, no Action Center task is ever raised, and a claim carrying a
> planted problem runs past its gateway and closes approved. A build measured before the app exists therefore
> fails **eight of the nine pinned runs** and the table it produces says nothing about the solution — it says the
> app is missing, which you already knew. Measured 2026-08-20; one build spent a full pass discovering it.
>
> What *is* worth running at block 5 is the clean claim, alone, which is that block's own acceptance gate.

**1. It stopped where it should.** A claim carrying a **screening-level** problem must reach the **screening
gateway**. A claim carrying a **review-level** problem must reach the **adjuster gateway**. A claim carrying both
reaches both, in that order. A **clean** claim must reach *neither* — it settles unattended and raises no task at
all.

That last one is the assertion builds get backwards, so state it as a count: **zero tasks on a clean claim is the
pass.** A task appearing for it is a failure even though nothing looks wrong on the screen.

**2. The right analysis is failing the right check.** Not "something was flagged" — the analysis that *owns* the
concern must be the one reporting it. Three analyses all reporting the same late notice is not three findings; it
is one finding and two scope violations, and it makes the reviewer's screen unreadable.

**3. The letter says it.** The manifest states what the claimant's letter has to mention. Check the letter text,
not the decision field.

> Assertion 3 exists because assertions 1 and 2 have both passed while the letter said something else entirely.
> A claim was approved, recorded as approved, and mailed a letter saying it "remains under specialist review",
> asking the claimant to itemise their cash and documents — under the subject line *"Your claim has been
> approved"*. Every field was right. Only the sentence the human reads was wrong.

**4. No payload was over the limit.** Every JSON column is capped at 10,000 characters, and going past it
**faults the claim at the write task** — it does not quietly cut the value (`contracts/claim-entity.md`, and the
silent-truncation claim that used to be there is retracted). So the primary symptom is a claim that died at its
last stage, and the secondary one is a length:

```bash
uip df records get <entity-id> <record-id> --output json    # then check the length of every *Json field
```

Any field whose length is exactly 10,000 would have been cut. Treat it as a failed run, not a near miss: the loss
lands in whichever payload was richest, which is the claim with the most damage rows — the interesting one.

> This assertion is temporary. It exists because the field type that would hold 128 KB is in private preview;
> when it arrives, the cap and this check go together. Until then it is the only thing standing between a
> silently halved policy document and a reviewer making a decision on it.

**5. Every payload actually holds something.** The same command, one more test, and it catches the defect the
other four are all blind to: **a column containing the four-character string `"null"`**.

That is what a defensive `JSON.stringify` binding writes when an agent output did not arrive
(`contracts/check-envelope.md`). It passes assertion 4 — it is not 10,000 characters. It passes assertions 1
and 2 — the claim stopped in the right place and the other analyses reported. It is invisible in every signal
until a human opens the tab it feeds. Measured on **6 claims in 49**, on `decisionJson`, which is the tab the
adjuster's gateway opens on.

So assert it mechanically: **every `*Json` column is either absent, or parses to something with content** —
never the literal `"null"`, never `""`, never `{}`.

```bash
uip df records get <entity-id> <record-id> --output json    # then, per *Json field:
#   absent            -> fine, if your design says nothing writes it on this route
#   "null" / "" / {}  -> FAIL. the pipeline ran perfectly and delivered an empty panel
#   length == 10000   -> FAIL, assertion 4
```

## What a clean claim proves

Run the clean scenario deliberately, and more than once. It is the assertion most solutions fail:

- every check passes, and the analyses say so rather than staying silent;
- **neither gateway appears — the claim raises no task at all** ([`pdd.md`](../pdd.md) §4);
- the record still shows a screening decision and a review decision, each recorded as *decided automatically*
  rather than left blank;
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

**6. The screen survives the claim.** This block is the only time you will have thirty-one different claims in
one place, and it is therefore the only chance to catch the defect that is invisible on one: **an agent payload
whose shape varies per claim.** Measured across 15 claims on one build, the policy blob came back six different
ways, two of which blank the reviewer's screen entirely — white page, minified stack, nothing else
(`contracts/record-payloads.md`).

**Do the shape audit first — it is the floor, and it does not need a browser.** Pull every claim's payloads off
the record and **count the distinct shapes** of each nested structure. Measured across 48 claims on one build:
the policy blob came back in 4 exclusion shapes, 4 `namedPerils`, 8 deductible, 8 endorsement and 11
coverage-section — and **three of those shapes silently emptied a panel on exactly one claim each.** No
five-claim sample finds a shape that occurs once in forty-eight. A variant that appears on one claim is not an
edge case here; it is a reviewer with a blank tab.

**Then open the screen, if you have a browser.** On at least five runs that raised a task — five *different*
claims, different scenarios, ideally different currencies — click through **every** tab. A screen that opens is
not a screen that renders: the panel that dies is one click further in, and it dies on the claim you did not
try.

A coding agent running headless, with no signed-in browser profile, **cannot do the second half** — and that is
an acceptable outcome as long as it is recorded as *not run* and the shape audit was done. Do not skip both and
call the assertion passed.

## How many, and in what order

**Start with one clean claim, before anything else.** It is the cheapest run in the set — five and a half
minutes measured — it is the only claim that exercises *both* automatic-decision paths end to end, and it is the
criterion this document already says most builds fail. It proves the spine. Only then fan out.

1. **One clean claim.** If it does not settle unattended, nothing below will tell you anything you can act on.
2. **One per problem, pinned** — nine runs. The coverage test, and the one to keep green.
3. **A second clean run**, once the nine are green — the fixes you made for them are exactly what re-breaks it.
4. **Then twenty on `random`**, unpinned, asserted against their own manifests.

The old order put the nine first, reasoning that a pinned failure names its own cause. True, and still expensive:
**every pinned failure is an agent fix and a redeploy**, so you pay a full deploy cycle before knowing whether
the spine works at all.

### This is a fix block, not a measurement block — budget for it

The nine **will not** pass first time. That is the point of the block: its whole purpose is finding checks that
are wrong, and a build that scores 9/9 on the first pass has almost certainly tested nothing.

Measured on the first build to finish this block: **first pass scored 5 of 9, and reaching 9 of 9 took eight
deploy cycles.** Eight of the nine rows needed a change before they passed. Only one of those changes was to the
case plan — the rest were **agent prompts and output schemas**.

So set the loop up before the first run and plan around it:

| | |
|---|---|
| pack + publish + deploy | ~4 minutes — in place, same deployment name, no uninstall (`CONFIG.md`) |
| one claim, end to end | ~6 minutes at a ten-second inspection poll |
| **one fix-and-verify round** | **~10 minutes — plan on eight of them** |

**Verify a fix on one claim, not on the set.** Aim a single pinned run at the check you just changed; keep the
full thirty-one for the end. And read the first red row as the block working, not as a disaster.

### What the twenty unaimed runs are actually for

They earn their place, but not for the reason you would guess. "Interactions surface" produced **one** genuinely
useful claim. What the twenty actually buy is **volume**: the payload-shape variance assertion 6 depends on,
several currencies, and claims carrying problems the answer key does not declare.

**They also raise about twenty human tasks, and you have to decide who answers them.** Answering twenty by hand
is not affordable and leaving them parked scores nothing, so **automate a stand-in reviewer** — follow the
recommendation, deny on a fatal screening check, and quote the failing checks in the note so the letter still
has a real reason. **Declare it in the results table**, so nobody later reads those rows as human judgement.

Run them concurrently. A claim spends most of its life waiting — and **check your inspection poll interval
before you start**, because it is paid once per run here rather than once per build. The stand-in models no
assessor delay at all (`contracts/provided-processes.md`), so a two-minute timer costs you an hour across
thirty-one claims for nothing. Ten seconds.

## Recording the result

For each run keep the claim id, what was aimed at, every assertion, and — when one fails — the actual text
the analysis produced. **The text matters more than the pass/fail.** An analysis that fails the right check for
the wrong reason will pass this test and mislead a reviewer on a real claim; the wording is the only place that
shows.

Keep the failures. A test pass that records only successes cannot tell you whether your solution got better.
