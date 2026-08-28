# The review task — what the case hands a person, and what they hand back

The shape of the two human gateways. **`3d-case` binds it and `3f-validation` renders it**, which is why it lives here rather than in either — and why it is settled from the design rather than discovered while building a screen.

## Why this is fixed before the Action App exists

**The case binds the app's *contract*, not its code.** An app registered with this shape and an empty page is enough for the case to wire both gateways, run a claim into them and prove the routing. The app's screens replace the empty page later and the case is never touched again.

That ordering is not a convenience. **Changing this shape after the case is bound is expensive**: it is a schema change, the app has to be re-registered to refresh its contract, and re-registering **clears the task's bindings at both gateways**. Whatever you decide, decide it once.

## The shape

| | Name | Type | Why it is where it is |
|---|---|---|---|
| **inOut** | `recordId` | string | The claim record's **row id**, not the claim number. The analysis columns are only readable by a by-id read, so this is the identifier the Action App actually needs |
| **inOut** | `claimId` | string | The claim number. Shown to the reviewer so they recognise it; **never used to fetch** |
| **inOut** | `triggerStage` | string | Which gateway raised this. Two values, and the Action App changes shape on it. **Never infer it** from which columns happen to be populated |
| **output** | `reviewDecision` | string | What they chose, recorded as data as well as routed on |
| **output** | `reviewerNotes` | string | Their reason, in their own words. Required at both gateways |
| **output** | `reviewedAt` | string | ISO timestamp, set on submit |
| **output** | `settlementJson` | string (JSON text) | **at the second gate**: the settlement as the adjuster confirmed it — the recommendation untouched plus one override per changed line with the original, the new value and the reason (`PDD.md` §7.8). Action Center keeps outputs on completion, so a decided task still shows the amounts |
| **outcome** | **exactly two** | — | What the case branches on. One means carry on, one means stop |

**Names match the claim record's columns** — `contracts/claim-entity.md`, *One name, three casings*. The task, the case variable and the column are the same word.

**How the case reads the outcome, because everything routes on it.** The chosen outcome comes back as a task output literally named **`Action`** — capital A, supplied by the platform, not declared by you alongside the others:

```
name: "Action"   →   var: "eligibilityDecision"      (source "=Action")
```

It is **not** called `outcome`, and no `$xref` is involved. Guessing wrong is expensive in a specific way: it resolves to nothing, every claim takes the same branch, and the plan looks correct.

**Everything else the Action App reads from the claim record, using `recordId`.** Do not thread the claim through the task payload — that is seventeen bindings at the second gateway, each able to arrive empty silently, carrying data the record already holds. It is also how a component's input budget is blown (`claim-entity.md`, *Two budgets*).

**There is no `json` type, so a document travels as a string.** The schema supports string / number / integer / boolean / array / object / file, and `object` is rejected unless every nested property is spelled out. Declare JSON payloads as **a string carrying JSON text** — which is also the shape the `MULTILINE_TEXT` column wants, so the case writes it with no conversion.

**An output you have nothing for is omitted, never sent as `""`** — an empty string replaces the column's content on the way to the record; absence leaves it (measured 2026-08-27 through the payload on the wire).

**The confirmed settlement is an output, not a record read**, because Action Center keeps outputs on completion and drops inputs — a *completed* task can still render the approved amounts. Never move anything out of the three inOuts. **The trap this sets for the screen** (measured 2026-08-27, route 4): the record's `settlementJson` column holds the **recommendation**; after an override the confirmed figures live in the task output and in `decisionJson.outcome.approvedSettlement`. A screen that renders the column after an override shows the pre-override amount.

## Two outcomes, and not three

**Exactly two at each gateway.** Carry on, or stop. Two gateways × two answers is **four routes**, and four is what `3e-run` proves and `4-verify` tests. A third outcome anywhere multiplies the matrix every later block carries, for a distinction that is not a route.

The tempting third is *partial approval*, and it is genuinely part of this process — but it is **a recommendation and a number, never a branch**. `PDD.md` §7.6 is explicit that the decision rules produce a recommendation, not an outcome, and the partiality lives in the amounts, on the record, in the letter. **Route on what the process does next, not on what the answer was about.**

## The decision is an outcome, the reason is an output

Outcomes are what the case branches on. Outputs are data the process carries onward. **Both must reach the claim record**, written by the case after the task completes — a gateway that completes and writes nothing looks identical to one that works, until someone asks what was decided last week.

## What survives completion, and the three ways it does not

**Completing a task drops its `inputs`. Only `inOuts` and `outputs` survive.** That is the whole reason the three identifiers are `inOut`: a decided task must still know which claim it belonged to, or it can never be re-opened.

Two more causes, and a build has to handle all three:

- **Anything that writes task data replaces the payload rather than merging** — the in-app save, the draft save, and `uip tasks complete --data`. Send only the outputs and you erase the `inOuts` the platform would have kept. **Read the current payload, spread it, then write. At every call site.**
- **Neither is retroactive.** A task decided before a fix stays broken, because its payload was written at completion and nothing rewrites it. **Test a fix against a freshly decided task, never an old one.**

So the Action App needs a floor: **if a decided task arrives with nothing identifying it, say so plainly and show the decision that did survive.** That is a real state the platform can hand you, not a malformed payload.

## The title is part of the contract

Action Center is one queue for the whole tenant. **The title names the gateway and the seat** — *"Eligibility review for `<seat>`"*, *"Claim review for `<seat>`"* — because twenty rows reading *"Eligibility review"* cannot be told apart, and a reviewer opening the wrong seat's claim is a confusing five minutes for two people.

The title is set where the task is raised, in the case.

## The casing depends on who completed the task

The names above are what the **app** sends. A task completed from the command line comes back **PascalCased** — you send `reviewerNotes`, `uip tasks get` echoes `ReviewerNotes`. The outcome is unaffected, so routing is identical.

**Map the names in this contract, and never re-point a mapping at what the CLI printed.** Two seats did exactly that on one round — one on a confident answer from the platform's own documentation tool — and produced a case that passes its own CLI tests and breaks the first time a human uses the screen. If your notes arrive empty, the fix is upstream of the mapping, not in it.

The same caution applies to the app: **do not capture a fixture from `uip tasks get`**, which PascalCases the whole payload for display. Read the three inOut identifiers through one case-tolerant lookup at the edge and write back the camelCase above — then a task answered from the CLI still opens, and one raised by the case still works.
