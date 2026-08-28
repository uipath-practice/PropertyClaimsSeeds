# The claim entity — one row per claim

The Data Fabric entity behind what `PDD.md` calls the claim record.

`PDD.md` §1.5 P5 asks for *"a store for the claim entity that outlives any single step and can be read while the claim is in flight"*. This is that store, and this schema is **pinned**.

**Pinned, and it is worth knowing why**, because the method would normally have you design it. Every later block — the agents, the case, the validation app — binds to these column names, and so does everything the maintainers compare a build against. Designing a thirty-six column table teaches little; losing every downstream recovery path costs a day. Design it yourself if you want the exercise, then reconcile against this before you create anything.

It is **yours to build, in your seat folder** — see [`CONFIG.md`](../CONFIG.md), *The claim entity*.

## One name, three casings — and a fourth on the way back

The same fact travels three surfaces and must keep one name:

| Surface | Form |
|---|---|
| what a component returns | `out_EligibilityChecksJSON` |
| the case variable | `eligibilityChecksJson` |
| the column here | `eligibilityChecksJson` |
| **what a record read returns** | **`EligibilityChecksJson`** — the platform PascalCases every column on the way out (`uip df records get`, `records list`, the app's SDK read), while `entities get` still reports `eligibilityChecksJson`. Measured 2026-08-27. Write camelCase; read case-tolerantly — an app keyed on `row.claimId` gets `undefined` and renders an empty screen with no error |

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
| `policyId` · `incidentType` · `propertyCountry` | `STRING` 100 | `propertyCountry` is on no field the extractor returns (`ClaimProperty` carries street, city, state, ZIP — no country) and no document states it as a field. Derive it at intake from the claim currency — `PDD.md` §12 V1 pairs the six countries with their currencies one to one — and write it once. Both measured designs did exactly this; record it as an SME item rather than re-deriving the question. |
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
| `decisionJson` | `MULTILINE_TEXT` 10000 | **written twice** — the recommendation before the gate opens, the outcome after it closes; **and on the path where no gate opens the outcome is still written**, from the recommendation, so `outcome.approvedSettlement` is readable on every settled row and is `{}` on a refusal, unconditionally (measured: it was empty on exactly the straight-through claims the success criteria count) |
| `reviewRequired` | `BOOLEAN` | |
| `reviewDecision` | `STRING` 100 | |
| `reviewerNotes` | `STRING` 4000 | |
| `reviewedAt` | `DATETIME_WITH_TZ` | |
| `decisionReason` | `STRING` 200 | |
| `claimResponseJson` | `MULTILINE_TEXT` 10000 | the letter |

**The two gates do not share columns.** Screening writes `eligibility*`; review writes `review*`. They shared them once and the second gate destroyed the first gate's record.

## Two budgets, and they are not the same number

**A column holds 10,000 characters** and an over-length write is **refused at the write, with the column named** — `The provided value for field [claimDataJson] is longer than length limit 10000`, nothing written, the claim faulted at that step (measured). So every producer budgets to **8,000**, which leaves room for a claim with more damage rows than usual.

**A component's inputs are capped all together, and the usable budget measures ~8,700.** So three 10,000-character columns cannot be handed to one consumer, however comfortably each fits its own column. Count what a consumer is given, not what each producer wrote.

**Over the cap the platform refuses the call — `400 The field InputArguments must be a string or array type with a maximum length of '10000'` — and the usable figure is ~8,700 because the serialised arguments carry escaping** (measured 2026-08-28 on 1.201, Opus03 at 3c: one agent budgeted 2,200 returned 5,281 and the next consumer was refused). On 1.199 the same overrun degraded silently — the job reported `Successful` and returned an empty field — so a build that meets neither symptom has not proven it fits: count, slice, and read the record.

**A slice guard at the consumer must be at least the producer's budget, and JSON envelopes are ordered conclusion-first.** Free text survives a cut; JSON cut mid-object arrives unparseable (measured 2026-08-27: a 1,500-character budget, a 1,200-character guard, a 1,458-character payload).

**A payload budget written into a producer's prompt is a request, not a contract.** One asking for 1,800 characters returned 7,262 and 6,687 on later runs of the same claim. If a downstream budget depends on it, enforce it in code after the component returns.

## The case writes this itself — you do not build a writer

*From here on this file speaks to `3d-case`, which writes the entity, and to `3f-validation`, which reads it. `3b-entity` needs only the tables and the casings above.*

**Write it from the case, with `execute-connector-activity` tasks.** The v1 reference populated its 39 columns from **seven** such tasks; this schema has 36 and has no writer component of any kind; `Record Eligibility Assessment` alone writes seventeen columns in one call. A separate component that exists only to write the record is a project to publish, deploy, version and bind for something the case already does.

**Two ways to read a payload, and they reach different depths.** A **bare binding path** — `=vars.claimData.claimant` — resolves **one level** and no further; `vars.claimData.claimant.email` does not (measured). A **`=js:` expression with optional chaining** is the form for anything deeper, and it must also survive the field shape the extraction really has — every field is an object `{ Value, Confidence }`, so the value is one level further down than the name suggests:

```
claimantName    =js:(vars.claimDataJson?.ClaimClaimant?.[0]?.Name?.Value)
claimFormPdfId  =js:(vars.claimFormPdf?.ID)
reviewRequired  =js:(vars.isEligible === false || vars.isComplete === false)
```

**Depth past one level is measured only for the bare path.** The `=js:` form is what the reference build will prove or refute; until then, a value the case reads in more than one place is surfaced as a plain scalar by the component that already produces it (`provided-processes.md`, *The extracted payload is deeply nested*) — cheaper than discovering at `3e-run` which reading was right.

So a *normaliser* component is not needed either. What **is** worth surfacing as a plain scalar is anything read in more than one place — and the component that already produces the value is where to surface it, not a new component downstream of it.

**Two things decide which activity version you need**, and getting it wrong costs a day: a **tenant-level** entity works with the default activities, a **folder-scoped** one needs the V3 form. Yours is folder-scoped (`CONFIG.md`), so see `3d-case/cookbook.md`, *Writing to a folder-scoped entity*.

## How the write actually behaves

**`claimId` is unique, and the platform enforces it.** A second row for the same claim is refused — `Value uniqueness violation … Error Number: 2627`, naming neither the claim nor the case — so a case re-run for a claim that already has a row faults on its very first write. Every run is a new claim, or the old row is deleted first (`3e-run/cookbook.md`).

**`DATE` accepts what the extraction emits.** `"2026-07-28T00:00:00"` goes in, `2026-07-28` comes out — bind `DateOfIncident.Value` straight through; a read-back comparison compares the date part. `DECIMAL` keeps cents, `DATETIME_WITH_TZ` keeps its offset to the millisecond, a 9,000-character `MULTILINE_TEXT` comes back byte-identical (all measured, 2026-08-27).

**It is a patch, not a replace**, and the three cases are not symmetric:

| You send | What happens |
|---|---|
| the field omitted | its content is **preserved** |
| `null` | its content is **destroyed** |
| `""` | its content is **destroyed**, silently, reporting `Result: Success` |

**An unset case variable resolves to an empty string**, which is the middle column with the worst reporting. So **every optional field needs its no-value case handled deliberately** — coalesce to omitted, never to blank — or a later stage quietly erases an earlier one's work.

## Two traps in expressions

**A bare binding path resolves one level, and that is the only depth proven.** `vars.claimData.claimant` works; `vars.claimData.claimant.email` does not. Deeper is a `=js:` expression with optional chaining (*Two ways to read a payload*, above) or, for anything read twice, a scalar surfaced by the step that produces it — see [`provided-processes.md`](provided-processes.md), *Extract Claim Data*.

**Every condition is evaluated once at case start**, before any step has run, when every variable is empty. So a condition that parses a JSON column has to survive being handed nothing: guard it (`|| '{}'`), or the whole claim faults at t=0 with an error naming a node that appears nowhere in your design.
