# Design — what bites

| Issue | Fix |
|---|---|
| Two conditions share a display name — *Stage started* on six tasks | Condition names are one pool across the whole case: stage entry, stage exit, task entry, case exit. The planner's audit does not check it; `uip maestro case validate` refuses it at `3d`. Name each for what it tests. |
| `validate --strict --sdd` rejects the task-output variables listed in *Case Variables*, and `check_sdd.py` BIND-7 fails when they are missing | List them in a `#### Task-output variables` subsection under `### Case Variables` — both gates read it there. Write each output row as a plain `Field -> outX`, nothing after it. |
| A lane enters on `selected-stage-exited` from a stage that marks itself complete | *Exited* never fires, and `3d-case/check_caseplan.py` reports the lane unreachable. Enter the lane on the origin's completion with a guard, and give the next primary stage the inverse guard. |

**Put every routing conclusion in a case condition over facts an Agent reports** — the aggregate bound the settlement, the settlement adds up, the claimant's account rules out its own cause (`3c-agents/cookbook.md`, *An Agent whose verdict routes a claim reports facts*). A conclusion left to a prompt is the one Verify spends its cycles on.

**Missing details is deliberately not wired** (PDD §8.1): give its one task `Required: Yes` and gate the stage's entry on a variable nothing sets. An all-optional stage under `required-tasks-completed` fails validate at `3d`.

## Reading the checker

`FAIL` reaches the built plan · `WARN` is worth a look and does not stop a build · `NOTE` is something it could not decide, which is never a pass.

**Read three rules before writing** — they shape how the document is written: `HANDOFF-3` (no SME item left `Blocking = yes`), `ACT-1` (how a gateway's task block names its Action output), `OWN-1` (the write-ownership matrix and the entity table name the same writers).

**Three ways a design passes both gates and still cannot be built:** `ARG-1` — an `rpa` task bound to an argument the automation does not have; read arguments from `uip or packages entry-points`, never from memory. `JS-1` — a helper in an `=js:` expression that nothing defines (`nowIso()`); the grammar has none, write it inline. `ACT-2` — a gateway whose outputs never map the platform's literal `Action`.

`NATURE-3` lists tasks it could not match to a PDD step; until it is zero, their types were not checked.
