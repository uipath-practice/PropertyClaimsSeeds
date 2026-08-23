# The claim record — one row per claim

Every claim gets exactly one Data Fabric row, created when the case starts and updated by each stage as it
learns something. It is what the reviewer's app reads, what the dashboard aggregates, and the only place the
whole claim exists in one piece — the case instance holds lifecycle, not content.

Build this in block 3. Blocks 5 and 6 bind to it, so the **names below are a contract, not a suggestion**.

## One name, three casings

This is the rule that makes the wiring mechanical. A piece of data keeps one name from the agent that produces
it to the column it lands in; only the casing changes, and it changes predictably:

| Where | Form | Example |
|---|---|---|
| Agent output | `out_` + PascalCase, acronyms upper | `out_EligibilityChecksJSON` |
| Agent input | `in_` + the same | `in_EligibilityChecksJSON` |
| Case variable | camelCase, acronyms **not** upper | `eligibilityChecksJson` |
| Entity column | **identical to the case variable** | `eligibilityChecksJson` |

So every write is a rename-only mapping, and every mapping is checkable by eye. Two consequences worth stating,
each with one legitimate exception:

- **An agent output with no matching column is data that will be lost** — unless the case uses it for control
  flow, which is a real reason for an output to exist. Say which it is; an output that is neither stored nor
  branched on is dead weight the model spent tokens producing.
- **A column with no producer stays empty forever**, and a panel bound to it stays blank. There is no good
  exception to this one.

**Do not improve these names.** A clearer name is a broken binding three blocks later, discovered on a live run.

**There are two claim payloads and they are not the same thing.** Extraction produces `claimIxpDataJson` — the
raw six-group output of the extraction model, shaped by the taxonomy. The eligibility analysis reads it and
emits `claimDataJson`, the claim reorganised for every later analysis to consume. Only the second one has a
column. Giving both the same name looks tidy and breaks block 5, where a case variable can hold one shape at a
time and the analysis would be reading the variable it is about to write.

The same distinction, for the record: `policyDataJson` and `assessmentReportJson` are *produced by analyses*
from source documents. They are outputs, not inputs, on the agent that creates them.

## The columns

`claimId` is the **business** key: `isRequired` and `isUnique`, and equal to the case's `ExternalId`. It is not the primary key and there is no schema option to make it one — Data Fabric always keeps its own system `Id` as the primary key, and every `records update` addresses a row by that `Id`, never by `claimId`. Do not go looking for an `isPrimaryKey` flag. Everything else has **one writer
per route** — the stage that first has the data on the path the claim actually took — and **only `claimId` is
required**; a row is created carrying three columns, so anything else marked required would break intake.

*Per route*, not *one writer full stop*, because two columns genuinely need two and the rule read literally
loses data on one of them. **`decisionReason`** is written by the claim review when a review happens, and by the
**screening denial** when the claim never gets that far — otherwise the one column a list view shows is empty on
exactly the claims that were refused. **`settlementJson`** carries the agent's `recommended` from the analysis
and the adjuster's `final` from the review. Both are still one writer on any single claim, which is the property
that matters: what this rule exists to prevent is two stages writing the same column on the **same** claim, which
is how gateway 2 destroyed gateway 1's record until 2026-08-10.

**The groups below are moments, not tasks.** A heading says when a column becomes known. It is not an
instruction to create a write task per heading — how many writes a plan should make, and where, is
`5-case/spec.md`, *How many writes*.

Types are Data Fabric's own. The suffix decides the two temporal ones: a column named `…Date` is a calendar date
(`DATE`), a column named `…At` is the instant something happened (`DATETIME_WITH_TZ`). Six further types are
accepted by the server and unusable in the UI — `3-claim-record/cookbook.md` names them.

**Every `STRING` needs an explicit `lengthLimit`, and two of them need a large one.** A `STRING` created without
one defaults to **200 characters** — confirmed by test — and a longer value is then **rejected**, taking the
whole write with it (measured 2026-08-23; the earlier claim that it truncated silently was inferred from
`MULTILINE_TEXT` and is retracted with it). The default is the hazard, not the failure mode. That is
harmless for a policy number and destructive for a human's reasoning:

| Column | Set it to | Why |
|---|---|---|
| `eligibilityNotes`, `reviewerNotes` | **4000** | a reviewer's own words, and the only place their reasoning survives. 200 cuts a paragraph mid-sentence and tells nobody. |
| `claimFormPdfName`, `policyPdfName`, `assessmentReportPdfName` | 500 | bucket filenames, comfortably |

**4000 is the `STRING` ceiling, not a suggestion.** The valid range is 1-4000 and 4001 is rejected at create, so
on those two columns "larger is fine" is false - and reaching for `MULTILINE_TEXT` to get more room silently
changes the type block 6 renders. The filename rows are the ones where a bigger number costs nothing.

The rest are yours, as long as you choose them rather than inherit them. **Tighter than the default is often
right** — a currency code needs 20, not 200 — and a limit you picked is one you will recognise when a value hits
it.

**`DECIMAL` needs `decimalPrecision: 2`, for exactly the same reason.** `totalClaimAmount` and `approvedPayout`
are money. The platform's `DECIMAL` takes a precision of 0-10 and the default is unstated; created without one,
every settlement on the record may be rounded to whole units - a silent, plausible-looking corruption of the one
number this whole exercise is about. Set it, then round-trip a value with cents and read it back.

Three parallel builds produced three different answers here before this paragraph existed, and two of them
capped a reviewer's notes at 200 characters without noticing.

### Written at intake, when the row is created

| Column | Type | Source |
|---|---|---|
| `claimId` | `STRING`, **key, required, unique** | the case `ExternalId` |
| `caseInstanceId` | `STRING` | `=js:metadata.InstanceId` — the case metadata carries exactly two usable fields, this and `ExternalId` |
| `status` | `STRING` | a lifecycle word your case sets; the dashboard filters on it |

Nothing else can be written here. The row is created *before* extraction and before the document retrievals, so
no extracted field and no document reference exists yet.

### Written after the eligibility analysis

**Seven of these are agent outputs; one is not.** The eligibility agent emits the seven scalars below as
separate outputs, for the reason in *Scalars are not extracted from blobs*. `policyId` arrives with the policy
retrieval, before any analysis runs.

`reviewRequired` is **not here** — it belongs to the claim-review stage. It is computed by the case from the
decision analysis's recommendation, so it cannot exist until that analysis has run, and it must be written
*before* the gateway that reads it opens. A column's presence in this table means a stage writes it,
never that an agent produces it.

| Column | Type | Column | Type |
|---|---|---|---|
| `claimantName` | `STRING` | `policyId` | `STRING` |
| `incidentType` | `STRING` | `totalClaimAmount` | `DECIMAL` |
| `incidentDate` | `DATE` | `currency` | `STRING` |
| `dateOfSubmission` | `DATE` | `propertyCountry` | `STRING` |


| Column | Type | Holds |
|---|---|---|
| `claimDataJson` | `MULTILINE_TEXT` · 10,000 | the extracted claim, structured |
| `policyDataJson` | `MULTILINE_TEXT` · 10,000 | the policy, structured |
| `eligibilityChecksJson` | `MULTILINE_TEXT` · 10,000 | the eligibility envelope |
| `claimFormPdfId` · `claimFormPdfName` | `STRING` | the claim form attachment |
| `policyPdfId` · `policyPdfName` | `STRING` | the policy attachment |

### Written when screening resolves — by a reviewer, or automatically

| Column | Type |
|---|---|
| `eligibilityDecision` | `STRING` |
| `eligibilityNotes` | `STRING` |
| `eligibilityReviewedAt` | `DATETIME_WITH_TZ` |

**All three are written on both routes**, because most claims never reach the reviewer (`pdd.md` §4): when all
five checks pass, the gateway does not open and the case fills these in itself. Give the automatic route a
decision value that says so in as many words rather than leaving the columns empty — block 6 renders them, the
letters read them, and an empty `eligibilityDecision` is indistinguishable from a claim that got stuck. The same
applies to `reviewDecision` at the second gateway.

### Written after the analyses

| Column | Type | Column | Type |
|---|---|---|---|
| `assessmentReportJson` | `MULTILINE_TEXT` · 10,000 | `credibilityChecksJson` | `MULTILINE_TEXT` · 10,000 |
| `assessmentReportValidationJson` | `MULTILINE_TEXT` · 10,000 | `settlementJson` | `MULTILINE_TEXT` · 10,000 |
| `coverageChecksJson` | `MULTILINE_TEXT` · 10,000 | `assessmentReportPdfId` · `assessmentReportPdfName` | `STRING` |
| `payoutChecksJson` | `MULTILINE_TEXT` · 10,000 | | |

`decisionJson` is **not** here. The decision analysis runs in claim review — see the next group.

### Written during claim review, and at closure

The decision analysis runs **in claim review**, not alongside the other analyses ([`pdd.md`](../pdd.md) §3): the
analyses establish the evidence, and the judgement that reads them belongs with the stage that records it. So
this stage writes **twice** — `decisionJson` when the stage opens, before the gateway, so the reviewer's screen
has something to read and the recommendation is on the record whether or not a human is asked; the rest when the
review closes.

| Column | Type | Column | Type |
|---|---|---|---|
| `decisionJson` *(written on open)* | `MULTILINE_TEXT` · 10,000 | `decisionReason` | `STRING`, ≤ 200 |
| `reviewRequired` | `BOOLEAN` | | |
| `reviewDecision` | `STRING` | | |
| `reviewerNotes` | `STRING` | `claimResponseJson` | `MULTILINE_TEXT` · 10,000 |
| `reviewedAt` | `DATETIME_WITH_TZ` | `closedAt` | `DATETIME_WITH_TZ` |
| `approvedPayout` | `DECIMAL` | | |

`decisionReason` is short and deliberately a plain string: it is the one outcome sentence a *list* view can show
without fetching every row, for the reason in the next section.

## Every JSON column is capped at 10,000 characters — design for 8,000

The eleven `*Json` columns are `MULTILINE_TEXT` with an explicit `lengthLimit: 10000`. **The ceiling is real and
measured.** What happens when you exceed it is **path-dependent and not settled**, so plan for the worse case:

**Going past it is loud on both paths that have been measured**, and the correction matters because this
document said the opposite until 2026-08-23:

| Write path | What happens past 10,000 |
|---|---|
| **The connector** your case writes through (`CreateEntityRecord_V3`) | **The whole case faults** — `The provided value for field [<column>] is longer than length limit 10000`. Not a lost payload: a dead claim. |
| **REST** (`uip df records insert/update`) | **Rejected, atomically** — `Result: Failure`, and the previous value survives intact. Measured 2026-08-23. |

There is **no silent truncation on either path.** That claim entered this document on 2026-08-18, was inferred
rather than measured, and propagated into three other files; it is retracted here. The practical consequence is
sharper, not softer — an over-long payload does not quietly cost you a panel, it **kills the claim at the write**,
so the budget below is what stands between a build and a run that dies at its last stage.

So the limit is not a formality, and it is not the agents' to discover at run time:

- **Budget 8,000 characters per payload**, not 10,000. The 20% is headroom for a claim with more damage rows
  than the one this was measured on — payload size scales with the claim, and the ceiling does not.
- **Say the budget in the agent's prompt**, and never in its output schema. A `maxLength` in an output schema
  is hard validation rather than a clamp: one over-long string faults the whole job instead of being retried.
  `4-agents/spec.md` has the rule.
- **Assert it in block 7.** The symptom to look for is a **faulted claim at a write task**, and a column
  sitting at exactly 10,000 if any path ever does cut rather than reject.

Two payloads sit near the line and need real editorial discipline in their prompts: the structured policy
(measured at 10.9 KB on a single claim — **over the ceiling as designed**) and the coverage findings (9.0 KB).
Both carry material no downstream consumer reads. Cutting what nothing consumes is the fix; truncating a JSON
string is not, because it produces something that no longer parses.

> **This is an interim shape.** A larger field type — `MULTILINE_MAX`, up to 131,072 UTF-16 bytes in one column —
> exists and is **gated off on this tenant**, confirmed by test on 2026-08-23:
> *"Cannot create MULTILINE_MAX field: the Multi-line (Max) feature is not enabled for this tenant."* It is not
> enableable on request. When the flag lands, these columns become that type and the budget disappears. Nothing else about the design changes, which is why it is worth building against the small
> ceiling now rather than waiting.

**There are eleven of these columns and no cap applies to them today.** The 10-column ceiling belongs to
`MULTILINE_MAX`, not to `MULTILINE_TEXT` — verified by creating all eleven in one call, which the platform
accepted without complaint. It becomes live again when the larger type ships: the design then moves nine of the
eleven to `MULTILINE_MAX` and leaves `decisionJson` and `claimResponseJson` on the small type, which is 9 of 10
with one slot spare. Worth knowing before anyone proposes a twelfth analysis payload.

## How the connector actually writes

The update operation is named *Replace* and uses PUT, which reads like "overwrite the whole record". **It does
not.** Measured behaviour, per column:

| The request body | Result |
|---|---|
| omits the column | **preserved** — measured on the connector *and* on the CLI |
| sends `null` | **content destroyed** on the CLI/REST path; unmeasured on the connector |
| sends `""` | **content destroyed, silently, with `Result: Success`** |
| sends a value | replaced |

So it is a **merge**, which is what makes per-stage partial writes possible at all — confirmed on the connector's
own `UpdateEntityRecord_V3` on 2026-08-22, where a body naming five columns left a sixth untouched.

**There is no safe sentinel: omitting the key is the only form measured safe.** The empty-string row is the live
trap, because **an unset case variable resolves to `""`, not `null`** — mapping a column whose variable has not
been produced yet erases whatever an earlier stage wrote, with no warning, and on a max-length column the loss is
invisible in any list view. Do not reach for `null` as the escape either: it destroyed the column too, on the one
path where anyone has measured it.

Two rules follow, and neither is optional:

- **A stage writes only the columns it produces.** Never map a column defensively "in case it is set".
- **Every update needs `recordId`**, and that is the row's Data Fabric `Id` — *not* `claimId`. Capture it from
  the create response into a case variable and thread it through every later stage. If it is ever lost, recover
  it by querying on `claimId` rather than creating a second row: `claimId` is unique, so a re-create fails.

## Two traps in expressions

**Casing differs by access path, in the same solution.** Business fields are camelCase through the connector
(`claimId`) but PascalCase through `uip df records get` (`ClaimId`). Entity *system* fields are PascalCase
everywhere, so the record id reads as `Id` — including in the connector's own response, which therefore mixes the
two in one object: `CreateEntityRecord_V3` returns `{"Id": …, "CreateTime": …, "claimId": …, "status": …}`, so
`=response.Id` is the right extraction for `recordId` and a renderer keyed on a single casing misses half the
fields. And a job **attachment** object spells its key `ID`, all caps.
Getting any of the three wrong yields `undefined` — which per the table above writes nothing, so it is safe;
but never coalesce a missing value to `""`, which erases.

**Scalars are not extracted from blobs.** Reading a header value out of an agent's JSON output inside a case
expression writes nothing at all — a two-level read into an agent `json` output does not resolve. That is why
the eligibility agent emits `claimantName`, `incidentType`, `incidentDate`, `dateOfSubmission`,
`totalClaimAmount`, `currency` and `propertyCountry` as **seven separate scalar outputs**, bound one-to-one.
Plain scalars are the only form proven to bind. The agent also does the typing — a number, not `HK$1,234.00`,
and ISO dates — because it knows the locale and a case expression should not have to parse.

**Seven is the example. The rule is: every value the case has to read out of a payload is *also* emitted as its
own top-level scalar output.** Otherwise a contract is asking for a copy by the one mechanism it forbids
elsewhere in this file. Worked through, that means the decision agent emits its recommendation and its reason as
scalars as well as inside `decisionJson`; the payout agent emits the net figure; the response agent emits the
letter's subject and body. Each of those is read by a case expression, a binding or a gate. Miss the rule and you
rediscover it once per payload, in block 5, after the plan is written.
