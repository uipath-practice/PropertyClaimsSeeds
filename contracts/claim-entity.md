# The claim entity — one row per claim

The Data Fabric entity behind what `PDD.md` calls the claim record.

`PDD.md` §1.5 P5 asks for *"a store for the claim entity that outlives any single step and can be read while the claim is in flight"*. This is that store, and this schema is **pinned**.

**Pinned, and it is worth knowing why**, because the method would normally have you design it. Every later checkpoint — the agents, the validation app — binds to these column names, so a seat that invents its own schema can no longer take any of them. Designing a thirty-six column table teaches little; losing every downstream recovery path costs a day. Design it yourself if you want the exercise, then reconcile against this before you create anything.

It is **yours to build, in your seat folder** — see [`CONFIG.md`](../CONFIG.md), *The claim entity*.

## One name, three casings

The same fact travels three surfaces and must keep one name:

| Surface | Form |
|---|---|
| what a component returns | `out_EligibilityChecksJSON` |
| the case variable | `eligibilityChecksJson` |
| the column here | `eligibilityChecksJson` |

**Do not improve any of the three.** Bindings resolve by name at run time, so a better name packs, deploys and runs — then fails on a live claim with an error naming neither the binding nor the name.

A payload carried between steps and never stored still has a name, and it is not yours to choose either: take it from the argument that produces it, read with `uip or packages entry-points`, never recalled from a plausible convention.

## The columns

Grouped by the moment they are written, because that ordering is the part that matters — **a column a human must see has to be written before their step opens** (`PDD.md` C3).

### At intake, when the row is created

| Column | Type | Source |
|---|---|---|
| `claimId` | `STRING` 100, **required, unique** | the case's external id. A business key, not the primary key — the platform keeps its own `Id` |
| `caseInstanceId` | `STRING` 100 | `=js:metadata.InstanceId`. Case metadata carries exactly two usable fields, this and `ExternalId` |
| `status` | `STRING` 100 | a lifecycle word your case sets; the dashboard filters on it |
| `claimantName` | `STRING` 200 | |
| `policyId` · `incidentType` · `propertyCountry` | `STRING` 100 | |
| `incidentDate` · `dateOfSubmission` | `DATE` | |
| `totalClaimAmount` | `DECIMAL`, precision 2 | |
| `currency` | `STRING` 20 | never converted (`PDD.md` A2) |

### After the eligibility checks

| Column | Type | Holds |
|---|---|---|
| `claimDataJson` | `MULTILINE_TEXT` 10000 | the extracted claim, structured |
| `policyDataJson` | `MULTILINE_TEXT` 10000 | the policy, structured |
| `eligibilityChecksJson` | `MULTILINE_TEXT` 10000 | all five checks, passes included |
| `claimFormPdfId` · `policyPdfId` | `STRING` 200 | attachment ids |
| `claimFormPdfName` · `policyPdfName` | `STRING` 500 | bucket filenames |

### When screening resolves — by a reviewer, or automatically

| Column | Type |
|---|---|
| `eligibilityDecision` | `STRING` 100 |
| `eligibilityNotes` | `STRING` 4000 |
| `eligibilityReviewedAt` | `DATETIME_WITH_TZ` |

**4000, not 200.** These are a reviewer's own words and the only place their reasoning survives; 200 cuts a paragraph mid-sentence and tells nobody it did.

### After the analyses

| Column | Type | Column | Type |
|---|---|---|---|
| `assessmentReportJson` | `MULTILINE_TEXT` 10000 | `credibilityChecksJson` | `MULTILINE_TEXT` 10000 |
| `assessmentReportValidationJson` | `MULTILINE_TEXT` 10000 | `settlementJson` | `MULTILINE_TEXT` 10000 |
| `coverageChecksJson` | `MULTILINE_TEXT` 10000 | `assessmentReportPdfId` | `STRING` 200 |
| `payoutChecksJson` | `MULTILINE_TEXT` 10000 | `assessmentReportPdfName` | `STRING` 500 |

### During claim review, and at closure

| Column | Type | Note |
|---|---|---|
| `decisionJson` | `MULTILINE_TEXT` 10000 | **written twice** — the recommendation before the gate opens, the outcome after it closes |
| `reviewRequired` | `BOOLEAN` | |
| `reviewDecision` | `STRING` 100 | |
| `reviewerNotes` | `STRING` 4000 | |
| `reviewedAt` | `DATETIME_WITH_TZ` | |
| `decisionReason` | `STRING` 200 | |
| `claimResponseJson` | `MULTILINE_TEXT` 10000 | the letter |

**The two gates do not share columns.** Screening writes `eligibility*`; review writes `review*`. They shared them once and the second gate destroyed the first gate's record.

## Two budgets, and they are not the same number

**A column holds 10,000 characters** and an over-length write **faults the whole claim** — not silently, but not recoverably either. So every producer budgets to **8,000**, which leaves room for a claim with more damage rows than usual.

**A component's inputs are capped all together, and the usable budget measures ~8,700.** So three 10,000-character columns cannot be handed to one consumer, however comfortably each fits its own column. Count what a consumer is given, not what each producer wrote.

**Over the cap it degrades silently — it does not refuse to start, and nothing anywhere says the word *cap*.** Measured on one live claim with four consumers at or over it (8,695 · 8,704 · 8,969 · 13,490): every job reported `State: Successful`, the case reported `Completed`, and one of them returned an empty list. That emptiness surfaced three components later as *unreadable*, and turned a claim that should have settled into an escalation. **You cannot watch for a start failure, because there isn't one.** The only place the truth is visible is the trace's `agentRun` start arguments — sum them per consumer, and do it before you believe a green run.

**A payload budget written into a producer's prompt is a request, not a contract.** One asking for 1,800 characters returned 7,262 and 6,687 on later runs of the same claim. If a downstream budget depends on it, enforce it in code after the component returns.

## The case writes this itself — you do not build a writer

**Write it from the case, with `execute-connector-activity` tasks.** The reference solution populates all 39 columns from **seven** such tasks and has no writer component of any kind; `Record Eligibility Assessment` alone writes seventeen columns in one call. A separate component that exists only to write the record is a project to publish, deploy, version and bind for something the case already does.

**Read nested payloads inline rather than flattening them first.** A `=js:` expression with optional chaining reaches as far as you need:

```
claimantName    =js:(vars.claimDataJson?.ClaimClaimant?.[0]?.Name)
claimFormPdfId  =js:(vars.claimFormPdf?.ID)
reviewRequired  =js:(vars.isEligible === false || vars.isComplete === false)
```

So a *normaliser* component is not needed either. What **is** worth surfacing as a plain scalar is anything read in more than one place — and the component that already produces the value is where to surface it, not a new component downstream of it.

**Two things decide which activity version you need**, and getting it wrong costs a day: a **tenant-level** entity works with the default activities, a **folder-scoped** one needs the V3 form. Yours is folder-scoped (`CONFIG.md`), so see `3d-case/cookbook.md`, *Writing to a folder-scoped entity*.

## How the write actually behaves

**It is a patch, not a replace**, and the three cases are not symmetric:

| You send | What happens |
|---|---|
| the field omitted | its content is **preserved** |
| `null` | its content is **destroyed** |
| `""` | its content is **destroyed**, silently, reporting `Result: Success` |

**An unset case variable resolves to an empty string**, which is the middle column with the worst reporting. So **every optional field needs its no-value case handled deliberately** — coalesce to omitted, never to blank — or a later stage quietly erases an earlier one's work.

## Two traps in expressions

**One level of property access is the only depth proven to resolve.** `vars.claimData.claimant` works; `vars.claimData.claimant.email` does not. Anything deeper has to be surfaced as a scalar by the step that produces it — see [`provided-processes.md`](provided-processes.md), *Extract Claim Data*.

**Every condition is evaluated once at case start**, before any step has run, when every variable is empty. So a condition that parses a JSON column has to survive being handed nothing: guard it (`|| '{}'`), or the whole claim faults at t=0 with an error naming a node that appears nowhere in your design.
