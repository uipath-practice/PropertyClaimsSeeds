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
