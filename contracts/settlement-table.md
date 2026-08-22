# The settlement table — the contract for amounts

**Decided 2026-08-10** from four real runs (`CLM-HO-73220723`, `…434`, `…435`, `…437`). The reviewer and the
claimant both need *numbers*; today every number exists only inside prose, so nothing can render, sum or audit
them. This file is the one place the shape is written down. The prompts, the app and the case plan reference it and
never restate it.

## Why prose is not enough — measured, not assumed

| Finding | Evidence |
|---|---|
| Check ids drift every run | 4 runs → 4 id sets: `covered_valuation` / `covered_item_valuation`, `settlement_basis` / `replacement_cost_basis`, `reasonableness_check` / `estimate_reasonableness` / `assessment_reasonableness`. The app can never own a label ([check-envelope.md](check-envelope.md) rule 1 is dead in practice). |
| Numbers live only in prose | `'40,000.00 lei used against a 1,200,000.00 lei limit'`. **18 of ~28 detail rows** in `…435` exist solely to restate arithmetic. |
| Coverage D is always zero | The generator has **no loss-of-use damage items in any of its 12 profiles**. Every payout still reports a zero row and compares it to a limit. |
| Limits never bind | Claims run **1–8%** of the dwelling limit. "Remaining limit" is inert until prior claims exist (ROADMAP, task 13) — which is exactly what makes that feature worth building. |
| Formats are asymmetric | Claim amounts are strings with symbols (`'HK$28,000.00'`); assessor amounts are raw numbers (`29424.1`). |

**The one thing that makes a per-item table safe:** the claim's `ClaimDamageInventory` and the assessor's
`RecommendedRepairs.ItemizedRepairSchedule` correspond **1:1, in order and in meaning**, in all four claims. No
fuzzy matching is required. Do **not** rely on index alone — match on meaning and treat a length mismatch as a
finding.

## The shape

One row per claim item, grouped by coverage section, section subtotals, and a footer that applies the deductible
**once**. Every amount is a **number**, never a formatted string; the currency is stated once for the document.

```
COVERAGE A — DWELLING                     limit 1,200,000   remaining 1,200,000
  Roof, 30 sqm tiles torn off        28,000   assessor 29,841   → 28,000
  Ceilings, two bedrooms            12,000   assessor 10,558   → 12,000
  subtotal A                                                      40,000
COVERAGE B — OTHER STRUCTURES               limit 120,000   remaining 120,000
  Detached garage crushed           35,000   assessor 39,039   → 35,000
  Fence, gate, pathway               6,500   assessor  7,166   →  6,500
  subtotal B                                                      41,500
COVERAGE C — PERSONAL PROPERTY              limit 720,000   remaining 720,000
  Attic clothing, books              8,000   assessor  7,938   →  8,000
  subtotal C                                                       8,000

  subtotal A+B+C                                                  89,500
  less deductible (once)                                          -8,000
  Coverage D (loss of use)                                             0
  NET PAYOUT                                                      81,500 RON
```

### Three modelling rules, each fixing a real trap

1. **The deductible is a footer line, not a column.** It applies **once** to A + B + C combined and **never** to D.
   A per-row deductible column either triple-counts it or requires an arbitrary allocation. If A+B+C falls below
   the deductible those coverages pay nothing — still a **valid covered claim that pays zero**, not a denial
   (`pdd.md` §5.3).
2. **"Not covered" and "limit exhausted" are different facts and must not both render as 0.** Every row carries
   `covered: true | false` and, when false, `exclusionReason`. The cap columns always state the truth.
3. **The binding cap knows its own source.** For a Coverage C row the cap may be the section limit, a category
   sublimit, or what prior claims have left. One `cap` number plus `capSource: "limit" | "sublimit" | "remaining"`,
   so the reviewer can see *why* a number was reduced.

### Row and document fields

| Field | Type | Notes |
|---|---|---|
| `section` | `"A" \| "B" \| "C" \| "D"` | **Agent judgement, not a lookup.** The claim's category prefix does not determine the section: `Structure - Garage` and `Structure - Landscaping/Fencing` are **B**; `Structure - Roof/Ceiling/Walls` are **A**. Only one category in the whole generator pool says `Other Structure -`. |
| `label` | string ≤ 60 | Human-facing, from the claim item. Never a payload field name. |
| `detail` | string ≤ 120 | The brief description as the claimant submitted it. |
| `claimed` | number | From the claim inventory, formatting stripped. |
| `assessorEstimate` | number \| null | From the itemised schedule. `null` when the assessor did not price that item. |
| `cap` / `capSource` | number / enum | See rule 3. |
| `covered` / `exclusionReason` | bool / string | See rule 2. |
| `payable` | number | The amount used for this row, **before** the deductible. |
| `basis` | `"RCV" \| "ACV"` | Per row, because an endorsement can apply unevenly. |
| document | `currency`, `subtotalABC`, `deductible`, `lossOfUse`, `net` | `net = subtotalABC − deductible + lossOfUse`. |

**Suppress a section with no rows and a zero subtotal** — that is what removes the always-empty Coverage D block
without hiding a D payment when one ever exists.

## Where it lives

`settlementJson` is one of the eleven `MULTILINE_TEXT` columns at 10,000 characters — see
[`claim-entity.md`](claim-entity.md), which owns the column list. **There is no `MULTILINE_MAX` budget to
manage.** An earlier version of this section reasoned at length about a 10-of-10 `MULTILINE_MAX` cap; that type
is a private preview not enabled on this tenant, and the entity design it described has been replaced. It read
as authoritative because it carried a date and a correction, which is exactly what made it expensive.

```jsonc
settlementJson = {
  "currency": "RON",
  "recommended": { "rows": [ … ], "subtotalABC": 89500, "deductible": 8000,
                   "lossOfUse": 0, "net": 81500,
                   "producedBy": "Claim Payout Calculation Agent" },
  "final":       { "rows": [ … ], "subtotalABC": 89500, "deductible": 8000,
                   "lossOfUse": 0, "net": 81500,
                   "source": "agent" | "assessor",
                   "decidedBy": "…", "decidedAt": "2026-08-10T…Z" },
  "overrides":   [ { "row": "Detached garage crushed", "from": 35000,
                     "to": 30000, "reason": "…" } ]
}
```

**`recommended` is never mutated.** The assessor's edits produce `final` plus one `overrides` entry each, which is
the whole audit story: what the agent proposed, what the human set, and why.

**`approvedPayout` carries `final.net`**, so a dashboard can sort on it without parsing. It has **one** writer,
and picking the wrong one is why it stayed empty on every claim for two weeks: the obvious candidate is the task
that records the adjuster's decision, and *that task does not run on a clean claim* — which is a third of them,
and now every claim that skips both gateways. Give the column to the task that **authorises the settlement in
the approved ending**, reading the human's override if there was one and the agent's figure otherwise. Both
routes then populate it, and `pdd.md` §3 says the same thing from the process side: authorising the settlement
*is* writing the approved amount.

## Who may write what

| Writer | Writes |
|---|---|
| Payout agent | `recommended`, as its **own top-level output `out_SettlementJSON`** — *not* nested inside `out_PayoutChecksJSON`. Lifting it out of another output would need `=js:(vars.outPayoutChecksJson?.settlement)`, a two-level read into an agent's `json` output, which is the **unproven** retracted rule 3b.6. A separate output binds with `=js:(vars.outSettlementJson)` — no property access at all. |
| Action App | `final` + `overrides`, as **task outputs** — outputs survive completion where inputs do not, so a completed task renders the table with no entity read |
| `Record Adjuster Decision` | copies `final` into the entity, and `final.net` into `approvedPayout` |

### The two gateways write different columns

What the two decisions *are* is `pdd.md` §4's table. What they write is this one, and getting it wrong is not
theoretical: they were writing the same three columns until 2026-08-10, so gateway 2 destroyed gateway 1's
record.

| | Gateway 1 — eligibility | Gateway 2 — final review |
|---|---|---|
| Writes | `eligibilityDecision`, `eligibilityNotes`, `eligibilityReviewedAt` | `reviewDecision`, `reviewerNotes`, `reviewedAt`, `settlementJson.final`, `approvedPayout` |

The app's wording follows the *process* distinction: at gateway 2 the action is
*"Approve and send for settlement"*, not "continue". A reviewer approving a payment should be told that is what
they are doing.

**When no gateway is raised** — a clean claim, which now skips *both* (`pdd.md` §4) — `final` is a copy of
`recommended` with `source: "agent"`. The letter must not distinguish the two cases; the audit trail must.

### The aggregate reduction has to be legible, not merely correct

The annual aggregate is the one cap a claimant cannot check for themselves (`pdd.md` §5.3), so a settlement cut
by it is the row most likely to be authorised blind. Measured: a claim correctly reduced from SGD 16,600 to
9,807 where the only evidence offered was *"One settled claim in this policy period"* — no claim number, no
amount, no date, and not one of the three numbers a reviewer needs anywhere on the record.

So the settlement document carries them beside `net`:

```jsonc
"aggregateLimit": 125000, "aggregateConsumed": 112693, "aggregateRemaining": 12307
```

and the `aggregate_limit` check's details name **the earlier claim's identifier and what it consumed**. A capped
row also has to say so in words — *"Annual aggregate exhausted"*, *"Reduced by the remaining aggregate"* —
because `"Not covered"` and `"limit exhausted"` are different facts and must not both render as `0.00`.

## Override bounds — enforced in the app

An edited amount is rejected when it exceeds **`max(claimed, assessorEstimate)`** or the row's `cap`. Bounded by
the policy is not enough on its own: a typo becomes an overpayment, and no insurer lets a settlement exceed what
either document supports. **Any override requires a reason** — that is what makes `overrides` an audit trail rather
than a diff. Below-value overrides are always allowed; an assessor may pay less.

## The finale — two letters, one input

The Response agent receives `final` and the outcome, and:

- **Approved / partially approved** — itemises the breakdown by section, states the deductible once, and gives the
  net figure and currency.
- **Denied** — explains the reasoning and **omits the table entirely**. A denial has no amounts to break down, and
  printing a zeroed table reads as a clerical error.

## Payout prompt: fixed check ids, and prose that stops restating numbers

The table carries every number, so the checks carry only **judgement**. Seven fixed ids, in this order — the same
closed-list discipline the eligibility agent already has, which is what ends the id drift:

`item_valuation` · `coverage_limits` · `sublimits` · `aggregate_limit` · `deductible` · `settlement_basis` ·
`reasonableness`

**`aggregate_limit` was added 2026-08-20**, after a build found the list had six ids and no home for the one
planted problem `pdd.md` §9 assigns to payout by that name. It is a distinct arithmetic step — §5.3 caps at the
section limits first and at what the annual aggregate has left third — so overloading `coverage_limits` would
have hidden it. On a claim with no prior claims it reports `pass` with "no prior claims found", never `warn`.

- **Never restate a number the table already shows.** A check says *why* a figure was chosen, not what it is.
- `summary` drops to **≤ 400 characters** — the reasoning, not a re-reading of the arithmetic. Measured range
  today: 627–952.
- Drop `payout_arithmetic` and `net_settlement` as checks: the footer *is* the arithmetic.
