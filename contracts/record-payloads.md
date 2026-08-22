# The structured records — the shapes that are not envelopes

Four of the seven analyses produce a **structured record** as well as a check envelope: the claim, the policy,
the assessment, the claim history. `check-envelope.md` says these "have their own shape" and, until now, nowhere
said what that shape was. So every consumer guessed, and the producer invented a new answer per claim.

**Measured on 2026-08-22, across 15 claims on one seat.** The eligibility agent's `policyDataJson` came back in
this many spellings of the same facts:

| The fact | Spellings observed | What it cost |
|---|---|---|
| the exclusions list | `"…"` (12) · `{category, wording}` (2) · `{title, wording}` (1) | **blank screen** — React refuses to render an object as text |
| the named perils | `["…"]` (14) · `{intro, perils[]}` (1) | **blank screen** — `.join` is not a function |
| the section limits | `coverageSections[]` · `coverages[]` · `coverages{dwelling, …}` | no coverage cards, no per-section limit in the settlement table |
| the deductible | `deductible{…}` · `deductibles{dwelling, …}` | deductible not shown |
| a sublimit's figure | `{category, limit}` · `{category, amount}` | figure silently missing |
| an endorsement's text | `summary` · `terms` · `wording` | text silently missing |

Two of those blank the page and four fail quietly. **All of them are claim-dependent**, which is what makes this
the worst class of defect in the exercise: the build passes every test you run and breaks on the first claim
that happens to come back the other way. It survives "the screen opens", because the screen *does* open — the
tab that dies is one click further in.

## The rule

**One spelling per fact, every list an array of objects, no bare strings and no objects keyed by data.**

An object keyed by section name (`coverages: {dwelling: …}`) reads well and cannot be iterated safely, because
the next claim's policy names its sections differently. An array of `{section, limit}` always can.

## `policyDataJson`

```json
{
  "policyNumber": "HO3-SG-88213",
  "policyholder": "Wei Ling Tan",
  "propertyAddress": "Flat B, 23/F, Tower 3, 118 Bedok Road, Singapore 469572",
  "effectiveDate": "2025-07-12",
  "expirationDate": "2026-07-11",
  "paymentStatus": "Current - Paid in Full",
  "currency": "SGD",
  "annualAggregate": 125000,
  "deductible": { "amount": 4000, "appliesTo": "Coverage A, B and C combined" },
  "coverageSections": [ { "section": "Coverage A - Dwelling", "limit": 500000 } ],
  "sublimits":  [ { "category": "Jewellery, watches and precious items", "limit": 5000 } ],
  "exclusions": [ { "title": "Water seepage", "wording": "the exact sentence, verbatim" } ],
  "namedPerils":  [ { "peril": "Theft", "wording": "…, or absent" } ],
  "endorsements": [ { "title": "Replacement cost", "wording": "…" } ]
}
```

- **`exclusions[].wording` and `endorsements[].wording` are verbatim**, not paraphrased. `pdd.md` §5.2 requires
  the coverage analysis to quote the sentence it relied on, and a paraphrase cannot be quoted.
- **`section` carries the whole label**, `"Coverage A - Dwelling"`, not the letter. Anything that needs the
  letter takes it on a word boundary — `"Coverage A — Dwelling".charAt(0)` is `C`, and filing the dwelling limit
  under Coverage C is a wrong number that never raises an error.
- **Amounts are numbers in `currency`.** Never a formatted string, never converted.
- `annualAggregate` is the policy's maximum for all property losses in one period. Payout needs it to explain a
  reduction, not merely to apply one (`pdd.md` §5.3).

## `assessmentReportJson`

```json
{
  "assessorName": "…", "assessorLicence": "…", "assessmentDate": "2026-07-18",
  "propertyAddress": "…", "incidentDate": "2026-07-11",
  "causeDetermination": "Burst pipe, upper floor",
  "observations": [ { "area": "Living room", "damage": "…" } ],
  "estimate": [ { "item": "Flooring", "amount": 8200 } ],
  "estimateTotal": 31546.92,
  "currency": "SGD",
  "authorised": true
}
```

Three parallel analyses read this and none of them reads the PDF, so a field missing here is a fact that reaches
nobody — one reader, three consumers (`pdd.md` §3).

## `claimDataJson` and `previousClaimsJson`

`claimDataJson` is the eligibility agent's re-shaping of the extraction output for everyone downstream: the same
facts, one level deep, with the seven typed columns lifted out as scalars (`check-envelope.md`). Its damage
inventory is `items: [ { "category": …, "description": …, "amount": … } ]`.

`previousClaimsJson` arrives from a provided process **as a string** and is the only source for the aggregate
calculation. Whatever the payout analysis carries forward must include each prior claim's **identifier, date and
settled amount** — `pdd.md` §9 requires the aggregate finding to *name the earlier claim*, and a settlement
reduced by 41% with the cause invisible is the row that section exists to prevent.

## Reading these on the screen

**Normalise once, at the edge where the payload is fetched — never in the components.** `6-app/spec.md` says
never to defensively re-parse a payload that arrived in the wrong shape, and that is right when there is a shape
to be wrong against. Where an upstream shape is still drifting, the honest reading is *one declared shape,
produced once* rather than six guesses scattered through the UI. Name every variant you handle in that one file,
so it is one function to delete when the producer is fixed.

**And put an error boundary around each panel anyway.** Without one, a single malformed field takes the whole
claim down and the reviewer sees a white page — the outcome `6-app/prompt.md` explicitly rules out. With one,
the failing panel says so by name and the reviewer can still read the claim and decide.
