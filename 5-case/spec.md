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

## Parallelism is grouping, not ordering

Task groups are a nested array and **the inner grouping is what expresses concurrency**. Three tasks listed in
sequence run in sequence, however independent they look. `pdd.md` §3 says which work is parallel; expressing it is
your job.

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

## Done when

```bash
python3 5-case/check_caseplan.py <path-to-caseplan.json>   # 0 problems
```

Then, on a real claim aimed with a known scenario (`7-testing/spec.md` has the aiming): the case reaches an
ending, every stage it entered shows complete, and the claim record carries a row whose columns were written by
the stages that own them.

A claim that ends `Running (With Faults)`, or one where a stage's tasks are all green and the next stage never
started, is a failure — not a slow success.
