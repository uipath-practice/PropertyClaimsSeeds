# The Action App's two screens — the layout is decided

What the Coded Action App must look like when it opens, settled here so that every seat's app can be checked against the same picture. **The regions are the contract; the styling is yours** (`brand.md`). Most of this was settled by measurement on working builds; where something is still open it says so.

`PDD.md` §5.7 says what each reviewer must see — *not a summary*. `contracts/review-task.md` says what the case hands the app and what the app hands back. This file says where it all goes on the page.

## One app, two gateways

The two reviews are the same job at different depths, so one Coded Action App serves both, and the `triggerStage` inOut tells it which it is (`review-task.md`). Two apps would double the work and guarantee they drift.

| Gateway (`triggerStage`) | Who | Opens when | What exists on the Data Fabric record by then | Outcomes |
|---|---|---|---|---|
| **Eligibility review** — H1 | eligibility reviewer | screening flagged the claim | the claim, the policy, the five screening checks with results and reasons | **Proceed** · **Refuse** |
| **Claim review** — H2 | claims adjuster | the decision recommendation asked for a human | all of the above, plus the assessor's report and its validation, coverage, the settlement line by line, credibility, the recommendation with every reason and confidence | **Approve** · **Deny** |

**At H1 the later sections render as explicitly unavailable** — *"after the inspection"* — not as empty panels and not as errors. This is the single most common way the app looks broken while working correctly. A column that has not been written is **absent from the record**, not `null` and not `""`; a plain truthy test is the right check and every *not yet* falls out of it.

## Where the data comes from

- **The claim: from the Data Fabric record, by `recordId`.** The task payload carries the three inOut identifiers and the outputs — nothing else (`review-task.md`, *Everything else the app reads from the claim record*). The app signs in through the shared read-only registration (`CONFIG.md`). **The record comes back PascalCased** — `ClaimId`, `SettlementJson` — while the schema is camelCase (`contracts/claim-entity.md`, *a fourth on the way back*); read case-tolerantly or every panel is empty with no error.
- **The stages: from your own `sdd.md` Section 2**, and the current one from the record's `status` column — never a list typed into the app, which drifts the first time either changes.
- **The three documents, twice over.** Their *content* as data — the extracted claim, the policy data, the assessor's report as the Agents read them, from the record's payload columns — rendered in the reviewer's language on their own tabs, so a claims officer looks a value up without opening anything. And the *originals*, on demand from the buckets the record's `*PdfName` columns name, behind a button — never rendered inline in the flow.

## The wireframe — H2, a 1440 × 900 window

```
┌─ header ──────────────────────────────────────────────────────────────────────┐
│ PCL-4675074 · J. Okafor · water damage · SGD 48,200 · policy PL-99213          │
│ Claim review for <seat>        recommends: escalate — aggregate limit  [Docs 3]│
├─ where the claim is ──────────────────────────────────────────────────────────┤
│ ✓ Intake ─ ✓ Eligibility screening ─ ✓ Awaiting inspection ─ ✓ Analysis ─      │
│ ▶ Claim review ─ ○ Approved                                                    │
├─ decision ────────────────────────────────────────────────────────────────────┤
│ [ Approve ]  [ Deny ]        reason (required): ▏                              │
├─ at a glance ─────────────────────────────────────────────────────────────────┤
│ ┌ THE CLAIM ───────────┐ ┌ THE POLICY ──────────┐ ┌ THE ASSESSOR ─┐ ┌ SETTLE… ┐│
│ │ Nothing flagged      │ │ In force on the day  │ │ Usable — mould│ │ 9,807   ││
│ │ at screening         │ │ of loss              │ │ work unpriced │ │ recomm. ││
│ │ Claimant   J. Okafor │ │ Type      HO-3       │ │ Assessor  I.D.│ │ Covered ││
│ │ Incident   03/07/26  │ │ Period    03/07/25 → │ │ Licence   RO-…│ │  12,307 ││
│ │ Filed      08/07/26  │ │ Premium   Paid full  │ │ Assessed  06/07│ │ Deduct. ││
│ │ Claimed    48,200    │ │ Dwelling  500,000    │ │ Estimate  48k │ │  2,500  ││
│ │ Items      4         │ │ Deductible 2,500     │ │ Cause     pipe│ │ Payable ││
│ │ [ claim form ]       │ │ [ policy ]           │ │ [ report ]    │ │  9,807  ││
│ └──────────────────────┘ └──────────────────────┘ └───────────────┘ └─────────┘│
├─ the checks ───────────────────────────┬─ the settlement and documents ────────┤
│ Eligibility · Report(1) · Coverage ·   │ Settlement · Correspondence(2) ·      │
│ Payout(2) · Credibility · Decision(3)  │ Claim form · Policy · Assessor's rep. │
│  ▾ Aggregate limit binds — SGD 2,493 of prior claims this year    escalate    │
│  ▸ 12 other checks passed                                                      │
└───────────────────────────────────────────────────────────────────────────────┘
                              ▲ fold — a 1440×900 window ends about here
```

At **H1** the same page: the header names *Eligibility review for `<seat>`*; the decision row reads **Proceed / Refuse**; the assessor and settlement cards say *after the inspection*; the checks strip holds the five screening checks and nothing else.

## What each region must carry

| Region | Must carry | Must not |
|---|---|---|
| **header** | the claim in one line — number, claimant, incident type, amount and currency, policy; who is reviewing and at which gateway; the recommendation | be a logo bar |
| **where the claim is** | every stage of *your* case, in order, the current one marked, everything before it ticked | invent stages, or show only the current one |
| **decision** | both outcomes and the required reason field, always reachable — by keyboard and assistive technology, not merely painted | sit at the bottom of the page; offer a third outcome |
| **at a glance** | one card per area — a **verdict headline** *and* the five-to-eight facts it rests on, as aligned label → value rows; the document button on the card it belongs to | be four empty boxes at H1 — say *after the inspection* |
| **the checks** | every check from every Agent, failures open, passes collapsed to a count that expands; the number of concerns on each tab | be a JSON dump, or a wall of green ticks |
| **the settlement** (H2) | every line — claimed, covered, each cap that bound it named, deductible once, payable — and, per `PDD.md` §7.8, the adjuster's override on any line within BR-61 with a required reason; what they confirm goes back as `settlementJson` | let a line change without a reason; let H1 see it |
| **correspondence** (tab, right after *Settlement*) | every letter sent to the claimant for this claim, as a thread in the order sent — date, recipient, subject, body — read from the tenant-level `ClaimCorrespondence` entity by `claimId` (`contracts/provided-processes.md`, *Client Notification*); the count on the tab; *No letter has been sent yet* where the query is empty. This is what a reviewer of a **closed** claim opens first | invent a letter; show the log line instead of the letter |
| **the documents as data** (tabs) | one tab per document — *Claim form*, *Policy*, *Assessor's report* — rendering the record's extracted payload for it the way the Agent tabs render their checks: labelled rows in the reviewer's language, sections collapsed to a count, every value the officer might look up without opening the PDF. Measured 2026-08-28: tabs that only linked out to the PDF sent every lookup to a four-page document | be a JSON dump; be an external link |
| **the originals** (buttons) | a button per document on the card it belongs to, opening the PDF over the page; *not available* where none exists yet | render a PDF inline in the flow (the Action Center host blocks `<embed>`/`<iframe>` anyway — `cookbook.md`) |

## In the reviewer's language

**Never render a payload field name, an enum token or a `camelCase` key.** Every string is prose for a claims handler: *"Recommendation: escalate"*, never `recommend_review`; *"Not eligible"*, never `isEligible: false`. Payload keys are a wire format. Map every enum to a phrase; give every panel a title someone in claims would recognise.

- **Show passing checks, not only failures.** Three problems and nothing else does not tell a reviewer whether the other twelve things were checked or skipped. `PDD.md` §5.7: *passes included*.
- **A verdict is not a fact — carry both.** *"In force on the day of loss"* is the headline; the policy period, the premium status, the section limit and the deductible are the rows under it. A validator checks conclusions; if the card is only prose, every check costs a click.
- **Group the tabs and count what is in them.** The Agents' checks on one side, the evidence — the settlement, the correspondence, the three documents as data — on the other, with a divider between. `Payout (2)` tells a reviewer where to go before they click.
- **When the decision is already made, say so at the top and name who made it** — outcome, timestamp, person, reason, no controls. Without the name it is a status, not an audit trail. **The name has to be on the record**: the `Task` object the app receives carries no completer identity (measured 2026-08-27 — `taskId, title, status, isReadOnly, action, data, folderId, folderName, theme`, nothing else), and the app's scopes are read-only, so it shows whatever `decisionJson.outcome.decidedBy` holds — a role unless the case wrote the user. Say which it is; never invent a name. A decided task must still open (`review-task.md`, *What survives completion*).

## Rules that are not optional

- **No mock data on any error path.** A failed read renders an error state that says what was looked for — *"The policy document could not be retrieved"*, never *"Error"*, never a placeholder claim. Local fixtures are fine when chosen by an explicit `import.meta.env.DEV` branch that the production build compiles out, and captured from a real record rather than written.
- **An error boundary per panel.** One malformed field in the policy payload must not take the claim, the checks and both buttons down with it. This is the defect class that passes every test: fifteen claims render, the sixteenth blanks, one tab further in. Open more than one claim, and open every tab.
- **Never defensively re-parse a payload that arrived in the wrong shape.** If it is wrong, the Agent upstream is wrong — fix it there and log it.
- **Two habits that wreck the page**, both seen on real builds: a single column down the page (cards belong side by side; use the width), and inline PDFs.

## It also has to look good, and that is a requirement

This app is nearly all of what anyone will ever see of the solution; everything else is a job log. Consistent spacing, a real type scale, restrained colour that means something (a failed check is not the same red as a delete button), aligned numbers, states that are obviously states — `brand.md` has the tokens. If it looks like a form generated from a schema, it is not finished. Keep it **simple and static** for this build: the layout above, no router, no client store, two screens — so that what is on the page can be checked against `PDD.md` §5.7 line by line. Design variations are a later exercise.

## Out of scope

The Process App — the in-flight portfolio view `PDD.md` §11 asks for — is a different frontend over the same record and a later block. Build the claim view as a component that takes a claim and a mode, and that block becomes cheap.
