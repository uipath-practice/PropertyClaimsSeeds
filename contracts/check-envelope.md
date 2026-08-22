# The check envelope — one shape for every analysis payload

**Scope: six of the seven analyses.** The envelope is what makes one prompt shape generate the agents and one
screen render any of them. Two things it does not cover:

- **A structured *record* an analysis also produces** — the claim, the policy, the assessment, the history — has
  its own shape and is not an envelope. Those shapes are pinned in [`record-payloads.md`](record-payloads.md).
- **The response analysis is exempt.** Its output is a letter a customer reads; `pdd.md` §7 says the letter
  explains and never analyses, and its column feeds the notification's subject and body. Wrapping it in
  verdict/headline/summary would either bury the letter inside a summary field or force a second output with no
  column. `claimResponseJson` is a record, in the same class as `claimDataJson`.

**Decided 2026-08-07.** Every `*ChecksJson` blob an agent produces uses this one shape, and the Action App renders it
with a single component. Written once here; the seven agent prompts reference it and never restate it.

## Why it exists

Before this, all seven blobs were declared `"type": "object"` with **no properties**, so nothing was pinned and the
shape lived only in prose inside each prompt. The app's renderer was therefore shape-driven — it walked whatever JSON
arrived and printed the producer's keys. That is why a reviewer saw `recommend_review` on screen: a generic renderer
can only ever show internal names. The fix is not to relabel in the UI, it is to stop rendering arbitrary JSON.

## The shape

```json
{
  "verdict": "pass | attention | fail",
  "headline": "one line a reviewer can act on, <= 80 chars",
  "summary": "the agent's reasoning, prose, <= 10000 chars",
  "flags": ["short phrases, <= 60 chars each, <= 5 of them"],
  "checks": [
    {
      "id": "policy_status",
      "label": "Policy status",
      "status": "pass | warn | fail",
      "verdict": "Current and paid",
      "details": [ { "label": "Claim address", "value": "Flat B, 23/F, Tower 3 …" } ]
    }
  ]
}
```

| Field | Budget | Notes |
|---|---|---|
| `verdict` | enum | Drives the tab dot. `attention` means "a human should look", not "failed". |
| `headline` | 80 | The grey box heading. The decision envelope's `headline` is also copied into the entity's `decisionReason`, the only reasoning text a dashboard row can show. |
| `summary` | 10 000 | Absorbs the former `out_*AnalysisSummary` outputs — one self-describing blob per analysis, no loose strings alongside it. |
| `flags` | 5 × 60 | Rendered above the checks, not inside them. |
| `checks[].id` | snake_case | Stable key. The app owns the label for ids it knows. **For the nine checks `pdd.md` §9 names, the id is that name in snake_case** — `policy status` → `policy_status`, `aggregate limit` → `aggregate_limit`. Not a synonym you prefer: two builds that call the same check `address_match` and `property_address` cannot be compared, and neither can be asserted by one test. |
| `checks[].label` | 30 | Sentence case, human-facing. Never a payload field name. |
| `checks[].status` | enum | `pass` renders collapsed and green; `warn`/`fail` render expanded, amber/red. |
| `checks[].verdict` | 80 | The one-liner beside the label. |
| `checks[].details` | 6 × 120 | Supplied for **every** check, passing ones included. A `pass` row renders collapsed and a `warn`/`fail` renders open, but a reviewer must still be able to expand a green check and see its evidence — the address-match example is a `pass` that carries three addresses. **Corrected 2026-08-09:** the prompts originally said not to bother with details on passing checks, which left green rows unexpandable. |
| `checks` | 8 | — |

## Declare it as an `object`, never as a `string`

The envelope is a **structured output**: `"type": "object"` with these properties spelled out in the schema. The
tempting alternative — declaring `out_CoverageChecksJSON` as a `string` because the entity column that stores it
is text — undoes the whole point of this document. A string has no properties, so nothing above can be enforced,
and the shape falls back to living in prose inside seven separate prompts. That is precisely the state described
under *Why it exists*, and it is what put `recommend_review` on a reviewer's screen.

Measured 2026-08-20: of three independent builds, the one that chose `string` produced seven agents with **no
pinned envelope in any schema** and passed every gate in block 4 regardless.

The conversion is the case plan's job and it is one expression each way — `"value": "coverageChecksJson"` writing
out, `"=js:(vars.coverageChecksJson || {})"` reading back in. Two payloads are **not** yours to choose, because a
provided process fixes them: `in_ClaimIXPDataJSON` arrives as an object and `in_PreviousClaimsJSON` as a string
(`provided-processes.md`).

Whatever you do, be consistent across all seven. An agent that emits an object into a payload the next agent
declares as a string packs, deploys, and faults on a live claim.

## Rules

1. **Labels: agent supplies, app overrides.** The agent sends both `id` and `label`. The app prefers its own label for
   ids it knows and falls back to the agent's for anything new. Fully agent-owned labels drift between runs
   ("Policy status" one claim, "Policy Status Check" the next), which reads as an unstable UI; fully app-owned labels
   need an app release for every new check.
2. **Budgets go in the prompt *and* the renderer — never in the schema.** State them in the system prompt so the
   agent aims for them, and clamp them in the component, because an LLM cannot be trusted to respect a character
   count. `maxLength` / `maxItems` / `minItems` in `outputSchema` are **hard validation**: one 81-character verdict
   Faults the entire job (*"Agent output did not match the expected schema"*). Measured 2026-08-09; `enum` and
   `required` stay. **Corrected 2026-08-10 — the strip
   was incomplete.** `maxLength` and `maxItems` went; **`minItems: 1` survived in six of the seven schemas** and was
   only found by auditing rather than trusting this file. Now removed. An empty `checks` array is a payload bug we
   want to *see* — the app already reports it as a contract violation — whereas `minItems` turns it into a faulted
   job that discards every other output the agent produced, including the settlement table.
3. **Evaluate every check; never stop at the first failure.** The previous prompts said *"if any check fails, stop and
   report the failure"*, which produced a one-row screen. The `verdict` still stops the *process* — but the reviewer
   sees all the evidence. **Aim for at most 2–3 failing checks per claim**; a wall of failures is noise, not signal.
4. **`pass` must be honest.** A check with no data available is not `pass`. Omit it, or mark it `warn` with a detail
   saying what was missing.
5. **One check covers one rule.** A check has exactly one `status`, and `details[]` rows carry no status of their
   own, so a check that bundles six independent rules can only report the worst of them. Measured: a decision
   agent's `escalation_rules` check bundled late filing, coverage ambiguity, claimed-vs-assessed, credibility,
   the dwelling threshold and the annual aggregate. One fired; the app rendered the whole card red above five
   rows each saying nothing was wrong, and the reviewer's reaction was *"everything seems passed but the block is
   red"*. The payout prompt already gets this right with seven single-purpose ids — the discipline exists, it was
   just never stated. Split aggregate checks.

## The seven typed claim facts — separate outputs, not a sub-object

Seven entity columns must stay filterable and sortable and therefore cannot live inside a blob
([claim-entity.md](claim-entity.md)): `claimantName`, `propertyCountry`, `incidentType`, `incidentDate`,
`dateOfSubmission`, `totalClaimAmount`, `currency`.

The eligibility agent emits each as **its own top-level output** — `out_ClaimantName`, `out_TotalClaimAmount`, and so
on — and the case plan binds them with `=js:(vars.outClaimantName)`. Two requirements on the values, both chosen to
keep parsing out of case expressions:

- **`out_TotalClaimAmount` is a number, not a formatted string.** The claim PDFs show `HK$1,234.00`; the entity column
  is `DECIMAL`. The agent strips the formatting because it knows the locale — an `=js:` expression should not have to.
- **Dates are ISO 8601.** The PDFs use `DD/MM/YYYY`. The column *types* are
  [claim-entity.md](claim-entity.md)'s to state and not this document's — a `…Date` column is a `DATE`,
  a `…At` column is a `DATETIME_WITH_TZ`. An earlier version of this line said otherwise and was wrong.

They are declared but **not `required`**: a missing key resolves to `undefined` and writes nothing, whereas a missing
*required* output faults the job. **Never coalesce one to `""`** — an empty string erases the column
— measured, not assumed.

> **Why seven outputs and not a `header` sub-object, settled 2026-08-09 across two deploy cycles.** The first design
> put them in a typed `header` block inside `claimDataJson`, and the agent produced it correctly — verified on a real
> run: ISO dates, ISO currency, `totalClaimAmount` as the number `48000` rather than `"RON 48,000.00"`. But **both**
> extraction forms left all seven columns empty: `=js:(vars.outClaimDataJson?.header?.x)` and the defensive
> `=js:((typeof vars.outClaimDataJson === 'string' ? JSON.parse(...) : ...)?.header?.x)`.
>
> One level of property access is fine — `vars.outClaimFormPdf?.ID` and `vars.caseRecord?.Id` populated from the same
> body. So it is not "expressions don't work"; it is a two-level read into an agent's `json` output that yields
> nothing. Depth or producer, we did not isolate — depth or producer, we did not isolate. Plain
> scalar variables demonstrably bind, so that is what we use, and `header` is gone from the blob — one producer, one
> place, no drift.

## The casing you get back depends on where you read it

`uip agent debug` returns the whole payload PascalCased — `out_CoverageChecksJSON` as `OutCoverageChecksJSON`,
and the envelope's own keys as `Verdict`, `Headline`, `Checks[].Id`. The keys above are the contract and the
screen is written against them; the CLI's normalisation is a display artefact of that one surface. Do not
re-point anything at what `agent debug` printed — see the same trap, in the other direction, in
[`review-task.md`](review-task.md).
