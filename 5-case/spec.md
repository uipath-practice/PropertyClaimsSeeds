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

## Two passes, and why

**You cannot deploy a case that binds an app you have not built.** Deploy validation derives the app package from
the case binding and refuses with `One or more properties are missing: [package]`. The review app is block 6.

So block 5 builds the plan **without the two human gateway tasks** — every stage, every agent, every process, both
endings — and proves it end to end on a claim that runs unattended. Block 6 adds the app, inserts the two action
tasks, and rewires the two stage exits that then finish on a different task.

**The two human-decision stages still exist, and keep their shape.** Do not collapse a stage because its gateway
task is not there yet: the eligibility screening stage and the claim review stage are where a human will stand,
and block 6 drops a task into each. A stage that has been merged away or made to complete instantly has to be
rebuilt rather than extended, and the entry and exit rules around it are the expensive part.

**What "shaped" has to mean, concretely.** In pass 1 a flagged claim reaches the review stage and stops there,
because the only thing that could move it on is a human who has not been asked. **That is the correct
behaviour, not a defect** — the stage is waiting for a task block 6 will add. What is a defect is not knowing
which of the two you are looking at, so decide it before you run anything:

- the clean exit is present and conditional — `reviewRequired === false` and nothing else;
- the flagged path has **no** exit yet, and no invented substitute — an auto-approve "for now", a timer that
  gives up, a second exit that fires on the same completion, are each a thing block 6 has to find and remove;
- **the acceptance run is a claim that takes the clean path.** A flagged claim parking forever proves nothing
  either way, which is why a claim with nothing wrong with it is what closes this block.

**Gateway 1 gets the same treatment**, and this has caught a build out. The section above reads as though it is
only about the final review, but the acceptance run requires *no human asked at either gateway* — so eligibility
screening also needs a clean, conditional exit in pass 1 and no invented substitute, and block 6 replaces both.

That is not a workaround. Proving the spine before inserting the humans is the cheaper order: a stuck claim in
pass 1 has one possible cause, and you will have learned the edit loop before you need it under pressure.

**Both endings still work in pass 1.** Nothing sets `adjusterDecision` when no human is asked, so every downstream
read is `(adjusterDecision || recommendedDecision)` — the human's word when there was one, the agent's when there
was not. Write that expression once and reuse it; two routes that drift apart is the failure this prevents.

## Stage exits and entries must match — the rule that costs deploy cycles

A stage can leave in two ways and they are **different events**:

| The source stage leaves by | The downstream entry must use |
|---|---|
| an exit rule with `marksStageComplete: true` | `selected-stage-completed` |
| exiting without marking complete | `selected-stage-exited` |

Both forms are legitimate — a poll loop the claim returns to should never mark itself complete, so what follows it
keys on its *exit*. **Only the mismatch is fatal**, and it fails in the worst possible way: every task green, no
error, no incident, no cursor, and the downstream stage simply never starts.

Three related mechanisms, each silent:

- **`required-tasks-completed` fires on the last *required* task, not the last task.** Anything sequenced behind
  it is cut off mid-stage.
- **An exit rule with `marksStageComplete: false` races the completion rule** when both key on the same task
  finishing. If the diverting exit wins, the stage exits without ever completing.
- **A stage that marks itself complete does not satisfy a `selected-stage-exited` rule.**

**So: name the finishing task.** Every stage exit should be `selected-tasks-completed` naming the task — or the
parallel group — that ends the stage, with `marksStageComplete: true`. It survives a task being deleted, and it
reads as what it is.

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

4. **The generator is not in your folder.** Every agent, process and app you build resolves inside the case's own
   folder, so an empty folder path is correct for them — which is exactly why the one task that needs an explicit
   folder is easy to miss. `CONFIG.md` names the folder the generator lives in. Get this wrong and the case faults
   in about five seconds with `170007 The job's associated process could not be found`, having executed nothing.

## Auto-settlement: fail towards the human

A claim with nothing flagged skips the *final* review and settles unattended. It never skips the eligibility
gateway (`pdd.md` §4).

The gate is **`reviewRequired !== false`, never `=== true`.** A missing or malformed value must route to a
reviewer; only an explicit `false` may skip. This is a one-character difference with a one-way consequence.

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

## The case header

The case app renders a configured header above the stage timeline, and it reads **case variables only** — no
entity access, no metadata traversal. Whatever it shows, some task must already have emitted.

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
  --folder-name <solution-folder> --parent-folder-path ClaimCase-<NN>
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
