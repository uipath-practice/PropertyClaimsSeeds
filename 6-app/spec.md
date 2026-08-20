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

### Absent has two encodings and neither is an error

The case binds every downstream input at gateway 1, to an empty expression. So **no key is ever missing** — all
of them arrive — and the value tells you:

| Declared type | Arrives as |
|---|---|
| `json` | `""` |
| `string` | `null` |

**"Is this section available" is a value test, never a key test.** An app that treats a missing discriminator as
fatal reports a contract error on a task that is working exactly as designed.

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

### Anything the reviewer should still see afterwards must be declared `inOut`

Completing a task **drops its `inputs`**. Only `inOuts` and `outputs` survive. So a decided task re-opened shows
whatever you put in those two places and nothing else.

Size is not the constraint — the full second-gateway payload measures 37.7 KB and moves fine. The cost is that
changing this is a **schema change**: the app has to be re-registered to refresh its contract, which clears the
task's bindings and forces a rewire at both gateways. Decide it once, before the first deploy, not after.

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

## The three documents

The claim form, the policy and the surveyor's report are reachable two different ways, and they fail differently
— `cookbook.md` compares them and recommends one. Two things are design decisions rather than mechanics:

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

## Out of scope

**The operations dashboard** — the portfolio view of every claim, with filters and KPIs — is a real part of the
solution and is not this block. This block is the two gateways only.
