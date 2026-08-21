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
| **outcome** | two | — | What the case branches on. One means carry on, one means stop. |

Anything else the screen needs, it reads from the claim record (`claim-entity.md`) using `recordId`. **Do not
thread the claim through the task payload** — that is seventeen bindings at the second gateway, each of which
can silently arrive empty, to carry data the record already holds.

A design may add outputs — a settlement the adjuster edited, say. Add them as **outputs**; never move something
out of the three inOuts.

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

The names in the table above are what the **app** sends. A task completed from the command line hands the same
fields back to the case **PascalCased** — `reviewerNotes` arrives as `ReviewerNotes`. The outcome is unaffected,
so routing is identical either way; only the data mapping differs.

This matters at the block 5 / block 6 seam. Block 5 answers its tasks from the CLI to prove the four routes, and
an output mapping written against the CLI's casing will fail the moment block 6's real screen submits. **Map the
names in this contract**, and treat a `null` reviewer note during block 5 as expected rather than as a mapping
bug. Observed on two independent seats, 2026-08-21.
