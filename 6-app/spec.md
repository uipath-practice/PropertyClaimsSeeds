# The reviewer's screen — the design decisions

What block 6 must be true of, and why. This is the layer between the business request in `prompt.md` and the
platform mechanics in `cookbook.md`: the choices a solution architect would have settled before anyone opened an
editor, with the reasoning, so you can tell which of them are load-bearing.

Most were settled by measurement on a working build. Where something is still open, it says so.

## One app, two gateways

The two reviews are the same job at different depths, so one app serves both and a **trigger-stage input** tells
it which it is. Two apps would double the work and guarantee they drift.

| Gateway | Opens when | What exists by then |
|---|---|---|
| **Eligibility** | screening flags a claim | the claim, the policy, the screening findings |
| **Final review** | the decision analysis asks for a human | all of the above, plus the surveyor's report and the four analyses |

**At the eligibility gateway the later sections must render as explicitly unavailable** — not as empty panels,
not as errors. This is the single most common way this screen looks broken while working correctly.

### Absent is normal, and how it arrives depends on where you read from

Two different encodings, and which one you meet is decided by the section below — read the claim from the record
and you get the first, thread it through the task payload and you get the second.

| Reading from | A value that does not exist yet arrives as |
|---|---|
| **the claim record** | **the key is absent from the object entirely** — not `null`, not `""` |
| a task payload input | the key is always present; `json` reads `""`, `string` reads `null` |

The record is the recommended source, so plan for the first: a plain truthy test on the field is the right check,
and every "not yet available" section falls out of it without special-casing. What must **not** happen either way
is a contract error — an app that treats an unwritten column as malformed reports a fault on a claim that is
working exactly as designed, at the gateway where most of the claim legitimately does not exist yet.

## Where the claim comes from — the record, not the task

The screen reads the claim from the **claim entity**, and the task payload carries only what identifies the row
and what the reviewer sends back.

This was the other way round first, and moving it was worth a release. A task payload has to be assembled by the
case plan, one binding per field, and every field the screen wants is a binding that can silently arrive empty —
seventeen of them at the second gateway. The entity row is written by the stage that produced each value and is
already the system of record for exactly this data (`contracts/claim-entity.md`). Reading it directly makes the
screen's correctness independent of the case plan's binding table.

**The consequence to design for:** the screen needs Data Fabric access, and that is a permission the app must
hold rather than merely request. `cookbook.md` has the failure mode, which is worth reading before you build
rather than after.

## What the reviewer sends back

The decision is a **task outcome**; the reason and the timestamp are **task outputs**.

That split is not cosmetic. Outcomes are what the case plan branches on, so the outcome is what routes the claim
to approved or denied. Outputs are data the process carries onward — and, unlike inputs, **outputs survive task
completion**, which is what lets a decided task still show what was decided.

- The decision is **fully two-way at both gateways**. A reviewer who can only agree is not a reviewer, and the
  recommendation being usually right is not an argument.
- The written reason is **required**. `pdd.md` §6 makes every downstream analysis read it and be bound by it; an
  empty reason is a gateway that told the rest of the process nothing.
- Both must reach the claim record. A screen that completes the task and writes nothing to the record looks
  identical to one that works, right up until someone asks what was decided last week.

### A decided task must still open, and three separate things conspire against it

**This is the most-failed requirement in this block.** Every build so far produced a screen that worked while a
task was waiting and showed an error, or nothing at all, once it had been decided. Three causes, and you have to
handle all three:

1. **Completion drops the task's `inputs`.** Only `inOuts` and `outputs` survive. So whatever identifies the
   claim — the record id, the claim number, which gateway this was — has to be declared **`inOut`**, or a decided
   task arrives with no idea which claim it belonged to.
2. **Anything that writes task data *replaces* the payload rather than merging into it.** The in-app save, the
   draft save and `uip tasks complete --data` all do this, so an `inOut` the platform would have preserved is
   erased by your own write. Read the current payload, spread it, then write — at **every** call site. A build
   that got rule 1 right and this one wrong looks exactly like a build that got rule 1 wrong.
3. **A task decided before you fixed either of those stays broken for ever.** Its payload was written at
   completion and nothing rewrites it. So do not judge a fix against an old task — decide a fresh one.

Because of 3, the screen also needs a floor: **if a decided task arrives with nothing to identify it, say so in
the reviewer's language and show the decision that did survive** — never a stack trace, never a blank page. That
is not defensive parsing; it is a real state the platform can hand you.

Getting the schema right early matters more here than elsewhere, because changing `inputs` to `inOuts` is a
**schema change**: the app has to be re-registered to refresh its contract, which clears the task's bindings and
forces a rewire at both gateways. Size is not the constraint — the full second-gateway payload measures 37.7 KB
and moves fine. Decide it before the first deploy, not after.

## Reading it, in the reviewer's language

**Never render a payload field name, an enum token or a `snake_case` key.** Every string on the screen is prose
written for a claims handler: *"Recommendation: review required"*, never `recommend_review`; *"Not eligible"*,
never `is_eligible: false`. Payload keys are a wire format.

This one is easy to under-rate and was caught on the first real review of a working app — the data was correct
and the screen still read like a debug dump. Map every enum to a phrase and give every panel a title someone in
claims would recognise.

Two more that follow from the same principle:

- **Show passing checks, not only failures.** A screen listing three problems and nothing else does not tell a
  reviewer whether the other twelve things were checked or skipped. `contracts/check-envelope.md` carries every
  check with its status for this reason; a passing one can render collapsed, but it has to be there and it has to
  open.
- **Guard every field against overflow.** Reviewer notes and analysis summaries are free text of unpredictable
  length.

## The shape of the screen

A reviewer opens this to make one decision, and the screen's job is to get them there. **Everything that decision
turns on is visible without scrolling; everything else is one click away.**

That is not a plea for brevity — a claim carries a lot of data and a reviewer sometimes needs all of it, so
scrolling for detail is entirely fine. What is not fine is a screen where the reviewer has to scroll before they
learn anything: who claimed, for how much, what the machine recommends, and what it thinks is wrong.

```
┌─ header ─────────────────────────────────────────────────────────────────────┐
│ CLM-4675074 · J. Okafor · water damage · £48,200 · policy PL-99213            │
│ Eligibility review for Jane          recommends: review required   [Documents]│
├─ decision ───────────────────────────────────────────────────────────────────┤
│ [ Approve ]  [ Deny ]      why: ▏                                            │
├─ at a glance ────────────────────────────────────────────────────────────────┤
│ ┌ Claim ───────┐ ┌ Policy ──────┐ ┌ Assessment ──┐ ┌ Settlement ──┐          │
│ │ 3 to look at │ │ in force     │ │ not yet      │ │ £41,880 net  │          │
│ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘          │
├─ the analyses ───────────────────────────────────────────────────────────────┤
│  Eligibility │ Coverage │ Payout │ Credibility │ Decision                     │
│  ▾ The policy lapsed 11 days before the incident date            not passed   │
│  ▸ 12 other checks passed                                                     │
└──────────────────────────────────────────────────────────────────────────────┘
                              ▲ fold — a 1440×900 window ends about here
```

The regions are the contract; the styling is yours. What each one has to hold:

| Region | Must carry | Must not |
|---|---|---|
| **header** | the claim in one line, who is reviewing it and at which gateway, the recommendation | be a logo bar |
| **decision** | both outcomes and the reason field, always reachable | sit at the bottom of the page |
| **at a glance** | one card per area, each stating its conclusion in a phrase | be four empty boxes at gateway 1 — say *"after the inspection"* |
| **the analyses** | every check, failures open, passes collapsed to a count that expands | be a JSON dump, or a wall of green ticks |
| **documents** | a button per document, opening over the page | render a PDF inline in the flow |

Two habits that wreck this, both seen on real builds:

- **A single column down the page.** Cards belong side by side and tabs belong across; a claim's four summaries
  stacked vertically push the analyses off the screen and the decision off the bottom. Use the width.
- **Inline PDFs.** A document viewer in the page flow is several screens tall and it is there on every claim,
  whether or not anyone opens it.

### It also has to look good, and that is a requirement

Unusual to write in a spec, and it is here on purpose: **this screen is nearly all of what anyone will ever see
of the solution.** Everything else is a job log. A reviewer who finds it ugly or cramped will not trust what it
tells them, and neither will the person you demonstrate it to.

So spend the effort: consistent spacing, a real type scale, restrained colour that means something (a failed
check is not the same red as a delete button), aligned numbers, states that are obviously states. If it looks
like a form generated from a schema, it is not finished — that is the same failure as rendering `recommend_review`
one level up.

## The claim view gets used twice — design it as a component

Beyond this block there is an **operations app**: a portfolio view of every claim, where opening one shows the
same claim — same summary, same checks, same documents — read-only, with no decision to make.

That is the same view, minus the controls. So build it as a claim view that **takes a claim and a mode**, and let
this block's screen be that view plus a decision panel. The two apps do not share a codebase and their data
arrives by different routes, so this is not a runtime dependency — it is one design decision, made now, that
stops the same screen being written twice and drifting.

The practical consequence for this block: keep the fetch at the edge and the rendering pure. A claim view that
calls the SDK from inside its panels cannot be reused by anything that gets its claim another way.

## The three documents

The claim form, the policy and the surveyor's report are reachable two different ways, and they fail differently
— `cookbook.md` compares them and recommends one. Three things are design decisions rather than mechanics:

- **A document opens on demand, in an overlay — never rendered inline in the page.** A PDF embedded in the flow
  of the screen pushes everything a reviewer actually decides on below the fold, and it does it on every claim
  whether or not anyone wanted to read the document. A button per document, opening over the page, closing back
  to where they were.
- **A document that should not exist yet is not an error.** At the eligibility gateway no surveyor has been out.
  The screen says the report is not available, and does not offer a button that fails.
- **When a document will not load, say what was looked for.** *"The policy document could not be retrieved"* is
  actionable; *"Error"* is not.

## No mock data, on any error path

**A failed call renders an error state.** Never sample data, never a placeholder claim, never a silent fallback.

This is the most important rule here and it is here because of what it cost: a prototype with a fallback looked
finished for months while its live path did not work. If you want sample data for local development, put it
behind an explicit flag that cannot be reached in a deployed app.

The same instinct one level down: **never defensively re-parse or unwrap a payload that arrived in the wrong
shape.** If it is wrong, the contract upstream is wrong — fix it there and say so. Defensive parsing in the UI
converts a loud, findable bug into a quiet, permanent one.

## The task has to be findable in a shared queue

Action Center is one list, and on this tenant it holds everybody's tasks. A queue of twenty rows all reading
*"Eligibility review"* is unusable, and it is what every build has produced so far.

**Give each task a title that names both the gateway and the seat** — *"Eligibility review for Jane"*,
*"Claim review for Jane"*. The title is set where the task is raised, in the case plan, not in the app. Put the
claim number in it too if it fits; the seat is what makes the row yours, the claim number is what makes it the
right one.

## Out of scope

**The operations dashboard** — the portfolio view of every claim, with filters and KPIs — is a real part of the
solution and is not this block, though *The claim view gets used twice* above is the decision that makes it cheap
when it comes. This block is the two gateways only.
