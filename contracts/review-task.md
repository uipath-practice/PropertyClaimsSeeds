# The review task — what the case hands a person, and what they hand back

The shape of the two human gateways. **Block 5 binds it and block 6 renders it**, which is why it lives here
rather than in either — and why it is settled from the design rather than discovered while building a screen.

## Why this is fixed before the screen exists

**The case plan binds the app's *contract*, not its code.** An app registered with this shape and an empty page
is enough for the case to wire both gateways, run a claim into them and prove the routing. The screen replaces
the empty page later and the case never has to be touched again.

That ordering is not a convenience. **Changing this shape after the case is bound is expensive**: it is a schema
change, the app has to be re-registered to refresh its registered contract, and re-registering **clears the
task's bindings at both gateways**. Whatever you decide here, decide it once.

## The shape

| | Name | Type | Why it is where it is |
|---|---|---|---|
| **inOut** | `recordId` | string | The claim record's row id. **`inOut`, not `input`** — see below. |
| **inOut** | `claimId` | string | The claim number, for the title and for a human to recognise. |
| **inOut** | `triggerStage` | string | Which gateway this is. Two values, and the screen changes shape on it. |
| **output** | `reviewerNotes` | string | The reviewer's reason, in their own words. Required at both gateways. |
| **output** | `decidedAt` | string | ISO timestamp, set when they submit. |
| **outcome** | **exactly two** | — | What the case branches on. One means carry on, one means stop. |

**How the case actually reads the outcome, because everything routes on it.** The chosen outcome comes back as a
task output literally named **`Action`** — capital A, supplied by the platform, not declared by you alongside
`reviewerNotes` and `decidedAt`. Bind it to a case variable like any other output:

```
name: "Action"   →   var: "eligibilityDecision"      (source "=Action")
```

and branch on `vars.eligibilityDecision`. It is **not** called `outcome`, and there is no `$xref` involved.
Measured on two independent builds on 2026-08-23, both running live through every route. Guessing the name here
is expensive in a specific way: a wrong one resolves to nothing, every claim takes the same branch, and the plan
looks correct.

Anything else the screen needs, it reads from the claim record (`claim-entity.md`) using `recordId`. **Do not
thread the claim through the task payload** — that is seventeen bindings at the second gateway, each of which
can silently arrive empty, to carry data the record already holds.

A design may add outputs — a settlement the adjuster edited, say. Add them as **outputs**; never move something
out of the three inOuts.

**There is no `json` type, so a document travels as a string.** A coded action app's schema supports
string / number / integer / boolean / array / object / file, and `object` is rejected outright unless you spell
out every nested property — which for the settlement document is about forty lines the screen then binds field
by field, against this contract's own rule about not threading data through the payload. Declare it as a
**string carrying JSON text**. That is also the shape the `MULTILINE_TEXT` column wants, so the case writes it
with no conversion.

### Two outcomes, and not three

**Exactly two at each gateway.** Carry on, or stop. Two gateways × two answers is **four routes**, and four is
what block 5 proves and block 7 tests. A third outcome anywhere is not one more case — it multiplies the matrix
every later block has to carry, for a distinction that is not a route.

The tempting third is *partial approval*, and it is genuinely part of this process — but it is **a
recommendation and a number, never a branch**. `pdd.md` §5.6 is explicit that the decision rules "produce a
recommendation, not an outcome; nothing here closes a claim", and `settlement-table.md` already carries
*approved / partially approved* as a property of the settlement. A reviewer who accepts a partial settlement is
carrying the claim on; the partiality lives in the amounts, on the record, in the letter. Route on what the
process does next, not on what the answer was about.

## The decision is an outcome, the reason is an output

Outcomes are what the case plan branches on, so the outcome is what routes the claim to approved or denied.
Outputs are data the process carries onward.

Both must reach the claim record, written by the case after the task completes. A gateway that completes and
writes nothing to the record looks identical to one that works, until someone asks what was decided last week.

## What survives completion, and the three ways it does not

**Completing a task drops its `inputs`. Only `inOuts` and `outputs` survive.** That is the whole reason the three
identifiers are `inOut`: a decided task must still know which claim it belonged to, or it can never be re-opened.

Two more causes, and a build has to handle all three:

- **Anything that writes task data replaces the payload rather than merging into it** — the in-app save, the
  draft save, and `uip tasks complete --data`. Send only the outputs and you erase the `inOuts` the platform
  would have kept. Read the current payload, spread it, then write. At every call site.
- **Neither is retroactive.** A task decided before a fix stays broken, because its payload was written at
  completion and nothing rewrites it. Test a fix against a freshly decided task, never an old one.

So the screen also needs a floor: **if a decided task arrives with nothing identifying it, say so plainly and
show the decision that did survive.** That is a real state the platform can hand you, not a malformed payload.

## The title is part of the contract

Action Center is one queue for the whole tenant. **The title names the gateway and the seat** — *"Eligibility
review for Jane"*, *"Claim review for Jane"* — because twenty rows reading *"Eligibility review"* cannot be told
apart, and a reviewer opening the wrong seat's claim is a confusing five minutes for two people.

The title is set where the task is raised, in the case plan.

## The casing depends on who completed the task

The names in the table above are what the **app** sends. A task completed from the command line comes back
**PascalCased** — you send `reviewerNotes`, and `uip tasks get` echoes `ReviewerNotes`. The outcome is unaffected
either way, so routing is identical.

**Re-measured 2026-08-22 on `uip` 1.199.0-preview.119, and the news is better than it was:** the case's output
mapping, written against this contract's camelCase, **did** populate the columns from a CLI-completed task. The
mapping appears to be case-insensitive on this version. An earlier version of this section told you to expect a
`null` reviewer note through block 5; that is no longer what happens, and believing it would make you ignore a
real gap or hunt a bug that is not there.

**What has not changed is the rule.** Map **the names in this contract** and never re-point a mapping at what
the CLI printed. Two seats did exactly that on 2026-08-21 — one on a confident answer from the platform's own
documentation tool — and produced a case that passes its own CLI tests and breaks the first time a human uses
the screen. If your notes arrive empty, the fix is upstream of the mapping, not in it.

The same caution applies to the app: **do not capture a fixture from `uip tasks get`**, which PascalCases the
whole payload for display. Read the three inOut identifiers through one case-tolerant lookup at the edge and
write back the camelCase in the table — then a task answered from the CLI still opens, and one raised by the
case still works.
