# The case plan — what must be true

The case plan is the spine: it decides what runs when, what waits for a human, what runs in parallel, and where
every piece of data goes. It is also the most failure-prone artifact in this build, because **bindings resolve by
name at run time** — a wrong name packs cleanly, deploys cleanly, and fails on a live claim.

**The plumbing already exists.** Six processes are deployed in your folder — the generator, extraction, the
policy and assessor-report fetches, prior claims, and notification. Their arguments, types and behaviour are
`contracts/provided-processes.md`, and every "how does a file get from a
bucket to a task" question is answered there. Building one of them yourself is the single most expensive mistake
available in this block; the work here is *assembly*.

Two facts from that contract shape the plan before you write a line of it. **The policy number comes out of
extraction**, so the policy fetch cannot run until the claim form has been read — which is what gives Intake its
shape. And **the assessor-report fetch returns a not-ready flag rather than failing**, which is what makes a
waiting stage possible at all.

**This document deliberately does not list the tasks.** `pdd.md` §3 says what happens in each stage and §5 says
what each analysis decides; turning that into stages, task groups and bindings is the exercise. What is written
down here is only what you could not derive: the platform mechanics that decide whether a plan that validates
also *runs*.

## Everything lives in one solution

The case, the seven agents and later the app are **one solution**, named for your seat (`CONFIG.md`). A case
binds agents by name **inside its own solution**, so an agent published separately is not reachable from the
case that needs it. If block 4 left your agents in a solution of their own, move them before you start here —
that is cheaper than discovering it at deploy time.

## The stand-in app, and why the gateways are built here

**You cannot deploy a case that binds an app that does not exist.** Deploy validation derives the app package
from the case binding and refuses with `One or more properties are missing: [package]`. That fact used to push
both human gateways into block 6 — build the spine now, add the people later.

**It no longer does, because what the case binds is the app's contract, not its screen.** An app registered with
the shape in `contracts/review-task.md` and an empty page satisfies the binding completely. Registering it is
minutes and involves no design: a name, the input and output declarations, publish, deploy. `cookbook.md` has the
commands.

So block 5 builds **the whole journey, including both stops**, and block 6 replaces an empty page with a real
one. Three reasons this is the right boundary, in the order they cost money:

1. **Changing the contract after the case binds it is expensive.** It is a schema change; the app must be
   re-registered to refresh its registered contract; and re-registering **clears the task's bindings at both
   gateways**. Settling the shape from the design — which is what `contracts/review-task.md` is — costs nothing
   now and cannot be done cheaply later.
2. **The human routes are the ones that carry bugs, and they were going untested.** When block 5 ended at the
   clean path, every gateway exit, every decision-to-ending rule and every write behind them was unproven until
   somebody built a screen. The first build to reach them found three real defects in one afternoon — a stage
   entry with no guard on the eligibility decision, an ending that fabricated a settlement for a denied claim,
   and a notification reading a variable nothing wrote.
3. **It keeps the case-plan edit loop in one block.** That loop — recompile, repack, uninstall, deploy — is the
   most trap-laden tooling in the exercise. Meeting it twice, in two blocks, the second of which is supposed to
   be about a screen, is the worst available arrangement.

**What the stand-in must be, and must not be.** It is a registered app whose contract is final and whose page is
empty. It must **not** be a substitute for the decision: no auto-approve "for now", no timer that gives up, no
second exit firing on the same completion. Each of those is a thing the next block has to find and remove, and
each hides whether the routing works.

A person answers it by hand for now — from the command line if that is all there is (`cookbook.md`). That is
enough to prove every route, and proving the routes is what this block is for.

**Both endings must work whether or not a human was asked.** A clean claim reaches the ending with nobody
touching it; a flagged one reaches an ending because somebody answered. So every downstream read is
`(adjusterDecision || recommendedDecision)` — the human's word when there was one, the agent's when there was
not. Write that expression once and reuse it; two routes that drift apart is the failure this prevents.

## Stage exits and entries must match — the rule that costs deploy cycles

A stage can leave in two ways and they are **different events**:

| The source stage leaves by | The downstream entry must use |
|---|---|
| an exit rule with `marksStageComplete: true` | `selected-stage-completed` |
| exiting without marking complete | `selected-stage-exited` |

Both forms are legitimate. **Only the mismatch is fatal**, and it fails in the worst possible way: every task
green, no error, no incident, no cursor, and the downstream stage simply never starts.

### A waiting stage loops *inside itself* — `return-to-origin` does not do what it sounds like

**Corrected 2026-08-22, measured.** `return-to-origin` does **not** re-enter the stage that carries it. It sends
the claim back to the stage it came *from*. An earlier version of this document built the whole `Awaiting
inspection` stage on the opposite reading — *"a poll loop the claim returns to"*, with a `not ready` exit of
`return-to-origin, itself`. What that actually does: the timer, the poll and the write run exactly once, the
not-ready exit fires, and the case then sits `Running` with **no cursor in the stage, no incident and every task
green**, forever.

Put the loop inside the stage instead:

- give the timer a **second entry rule** — `selected-tasks-completed(<the write task>)` `IF reportReady !== true`
- give the stage a **single exit**, gated on `reportReady === true`
- set the timer to **10 seconds**, not minutes. The stand-in models no assessor delay — it answers ready about
  four times in five on every call, so the interval *is* the wait (`5-case/cookbook.md`).

That also keeps the status column honestly reading *Awaiting inspection* for as long as the claim is really
waiting, which the diverting-exit shape does not.

Three related mechanisms, each silent:

- **`required-tasks-completed` fires on the last *required* task, not the last task.** Anything sequenced behind
  it is cut off mid-stage.
- **An exit rule with `marksStageComplete: false` races the completion rule** when both key on the same task
  finishing. If the diverting exit wins, the stage exits without ever completing.
- **A stage that marks itself complete does not satisfy a `selected-stage-exited` rule.**

**So: name the finishing task, and let the tool decide the rule.** Every stage exit names the task — or the
parallel group — that ends the stage, and marks the stage complete.

**Three authorities disagree on the exact pairing, so know which one wins.** This document used to mandate
`selected-tasks-completed` **with** `marksStageComplete: true`; the case skill's own rules call that pairing a
schema error and require `required-tasks-completed` there; and `5-case/check_caseplan.py` rejects the skill's
alternative diverting-exit shape as unreachable. Exactly one shape satisfies all three, and it is the one to
build:

> `required-tasks-completed` + `marksStageComplete: true` on every exit · **no routing exits anywhere** ·
> branching expressed in the *downstream* stage's entry condition.

When the seed and the tool disagree, the tool wins and the disagreement is a finding (`AGENTS.md`). This row is
here because two builds have now spent a cycle rediscovering it.

The fix for a branch is never to key the diverting exit on an earlier task; that only moves the race. **Delete the
diverting exit** and let both destinations key on the *same* completion with mutually exclusive conditions — one
event, two tests, nothing to race. `pdd.md` §3 states this as a process rule; this is what it means structurally.

**Give each stage exactly one way in.** Two entry conditions that can both become true is a double execution.

**And every stage has a way in at all — with exactly one exception, which `pdd.md` names.** A stage nothing
enters is normally a defect: a branch you started and abandoned, or work you thought of and did not design. It
draws as a dead box, and the next person cannot tell it from a transition you forgot to wire.

The exception is **`Missing details`**. `pdd.md` §3 asks for it as a placeholder — *"it must exist in the
lifecycle and must not do anything yet"* — so build it with no tasks and no wired entry, and expect
`case validate` to warn about it on every run. **That warning is correct and you should not silence it**, by
inventing an entry condition or by deleting the stage. Say in your design that it is deliberate; then a reviewer
counting warnings knows which one is expected and which one is new.

## Conditions are the only description of the flow

**Edges are retired.** `edges` stays `[]`, no `Edge` or `TriggerEdge` object is ever authored, and a stage is
entered by its **entry conditions** alone. Nothing on the canvas carries flow information that the conditions do
not already carry.

That makes the conditions load-bearing in a way they were not when a picture existed alongside them. **Every
stage other than the first needs an entry condition naming a predecessor**, and one that does not is not a
missing line — it is a stage the case can never reach, rendering identically to one it can. The symptom is
*"The case manager returned no actions to execute"*: the engine evaluated everything, found nothing runnable,
and stopped with every task green.

**`layout` is the only thing left that is purely visual**, and it is worth writing rather than leaving empty —
`5-case/cookbook.md` has the arrangement. A map that names *some* stages and omits one is what crashes the
designer on load, so it is all of them or none.

## Parallelism is grouping, not ordering

Task groups are a nested array and **the inner grouping is what expresses concurrency**. Three tasks listed in
sequence run in sequence, however independent they look. `pdd.md` §3 says which work is parallel; expressing it is
your job.

**Do not reach for `runs-sequentially` to say it.** That rule must be a task's *only* entry condition, which
means a stage where four tasks form a chain and a fifth runs alongside them cannot be expressed with it at all —
and two of this process's stages are exactly that shape. Name the predecessor with `selected-tasks-completed`
instead: it is unambiguous, it survives a task being deleted, and it is what the rest of your plan already uses.

## Three shapes the schema insists on

These are not style. Each one was found by a live run failing in a way that named nothing useful.

**A JSON payload variable is `"type": "jsonSchema"`, never `"object"`.** The agents' own schemas use JSON Schema
convention where `object` is right, and copying that into a case variable is the natural mistake. The case
engine then **rejects the task before dispatch, silently** — no Orchestrator job is created at all, the element
just reads `Failed`, and `case instance incidents` has nothing to say. `object` is legitimate only *inside* a
nested schema body, describing a shape; never as a variable's or a task output's own type.

**A file output binds with `target: "=orchestrator.JobAttachments"`.** The ordinary
`target: "=<variable>"` shape is right for scalars and JSON payloads and wrong for files: you get an incident
reading `[400300] Error evaluating expression in activity inputs: Failed to evaluate expression: =<yourVar>`,
again before any job exists. Keep `var`/`id` pointing at your case variable — only `target` changes.

**The claim id is the case's own external id, not an input.** The case takes two arguments, `scenario` and
`discrepancy` (`7-testing/`), and nothing else. Set a `caseIdentifier` prefix and let the platform mint
`<PREFIX>-<generated>`; read it wherever it is needed as `=js:metadata.ExternalId`. Adding a `claimId`
in-argument means the caller has to invent an id the platform is already generating, and every downstream
consumer then has two sources of truth for the same thing.

## The four things a generated plan gets wrong

1. **Variable initialisers.** A stage whose entry condition reads a variable cannot evaluate on the first pass
   unless something has already set it. The platform's mechanism is an output entry marked `custom: true`,
   carrying a literal value and pointing at the task that will later produce it for real. It looks redundant and
   it is load-bearing — without it the condition reads `undefined` and the stage never opens.

2. **`=metadata.X` is not resolved at run time.** There is no `=metadata.` branch in the lookup path, so the
   plain form arrives at the consumer as the literal string. Always `=js:metadata.X`. The designer's picker offers
   the plain form; that is a UI hint, not a runtime contract.

3. **A skippable gateway deadlocks whatever follows it.** When a gateway can be skipped, the task after it needs
   **two** entry rules — after the gateway completes, *or* after the upstream task completes with the skip
   condition true. With only the first, the skipped path stops dead.

4. **The six provided processes are not in your folder — all six.** Every agent, process and app *you* build
   resolves inside the case's own folder, so an empty folder path is correct for them. That is exactly what makes
   the exception easy to under-apply: it is not one task, it is **every binding to a provided process**
   (`contracts/provided-processes.md`). Name the folder explicitly on each. Miss one and the case faults in about
   five seconds with `170007 The job's associated process could not be found`, having executed nothing — and a
   build that named the folder on the generator alone takes that fault on its second process task, not its
   first.

## Two skippable gateways: fail towards the human

**Both** gateways are skippable and a clean claim skips both, so it closes with no task raised (`pdd.md` §4, §9).
Screening opens the eligibility gateway only when one of the five checks failed; claim review opens the
adjuster's only when the analyses raise something.

Each gate is a **`!== false`** test, never `=== true`. A missing or malformed value must route to a reviewer;
only an explicit `false` may skip. This is a one-character difference with a one-way consequence.

**Gate on the case variable, not on the column you just wrote.** The screening verdict and `reviewRequired` are
both produced by an agent task *and* written to the record, and this document's own warning about reading back a
value written in the same batch applies to both. Bind each gate to the case variable the agent task produced.

Three consequences, and the first two are where builds break:

- **Every task after a skippable gateway needs two entry rules** — after the gateway completes, *or* after the
  upstream task completes with the skip condition true. This now applies to the step after screening as well as
  the step after review. With only the first rule, the skipped path stops dead — item 3 above, twice over.
- **The skip route still has to write the decision down.** `eligibilityDecision` and `reviewDecision` are what
  block 6 renders and what the letters read; a claim that skipped a gateway must record an explicit
  *decided automatically* rather than leaving the column empty. An empty column is indistinguishable from a
  claim that got lost.
- **Your acceptance run needs an aimed claim.** A clean one proves the automation and shows you no screen.

## The claim record is written through a shared connection

The Data Fabric connection is shared and lives in the `Shared` folder; your entity lives in **your seat folder**
(`CONFIG.md`). That combination is the one place where the connector's defaults are wrong for this build — the
activities it reaches for resolve entity names at tenant level and will not find yours, deploying cleanly and
faulting on the first row. `5-case/cookbook.md` has the six-line correction. Apply it to every write task, not
the first one you test.

## Every stage writes what it learned

The case instance holds lifecycle, not content — no API exposes task output payloads, so **anything a human or an
app must see has to be written to the claim record as it is produced.** `contracts/claim-entity.md` says which
columns each stage can write and why a stage may only write what it produces.

Two consequences for the plan's shape:

- **A recommendation must be recorded before the gateway that shows it opens.** A screen is built from what has
  been written down; a value written afterwards is one nobody can see.
- **A single write at the end cannot work.** The gateways fire before the case ends.

## The case header — authored in the designer, after your last pack

The case app renders a configured header above the stage timeline, and it reads **case variables only** — no
entity access, no metadata traversal. Whatever it shows, some task must already have emitted.

**There is no header field in the case schema.** Nothing on the root or on `metadata` holds it, so a locally
authored plan cannot carry one and a local `case pack` would drop it if it could. Treat this section as
something you do in Studio Web *after* the last time you pack — or skip it and say you skipped it. Do not invent
a field for it.

**Scalars only.** Binding an object renders as a literal class name, which is the most common way to make the
header look broken. Two sections of about seven rows is the practical maximum. Keep every expression null-safe or
an unstarted claim shows errors.

Worth doing well: the second section is most useful as the **case's own progress** — what each decider said and
where the claim has got to — rather than more claim data, which the first section already carries.

## Deploy into your own folder, never the tenant root

A solution deployment **creates a folder**, and if you do not say where, it is created at the tenant root — next
to every other participant's, and outside the seat that holds your processes and buckets. Two of them collide
into `ClaimCase-01`, `ClaimCase-01 1`, and it is not obvious afterwards which is yours.

Name the parent explicitly, every time:

```bash
uip solution deploy run --package-name <pkg> --package-version <v> \
  --folder-name <solution-folder> --parent-folder-path ClaimCase-<seat>
```

This is the same fact as *a solution folder is not the same folder*, seen from the other side: the deployment
creates a **child** of your seat, and that child does not inherit the seat's processes or buckets — so bindings
still need their folder named. Getting the parent right does not remove that; it just keeps your work where you
can find it.

## Done when

```bash
python3 5-case/check_caseplan.py <path-to-caseplan.json>   # 0 problems
```

Then, on a real claim aimed with a known scenario (`7-testing/spec.md` has the aiming): the case reaches an
ending, every stage it entered shows complete, and the claim record carries a row whose columns were written by
the stages that own them.

A claim that ends `Running (With Faults)`, or one where a stage's tasks are all green and the next stage never
started, is a failure — not a slow success.
