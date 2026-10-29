# Design

## How it is built here

- **Run the planner autonomous, design only**: no task list, nothing built, nothing deployed. `sdd.md` sits at the seed's root and its handoff header carries `Tasks file: tasks.md`, where `2-plan` writes.
- **Task types come from the PDD's §5.3 decision-nature column**, never from what the tenant holds. Name the step in each task's *Design Rationale* (`PDD step 4.3`): the checker matches types on it (`NATURE-3`).
- **Components are exactly `contracts/components.md`**: seven Agents and one Coded Action App; no tools, no evaluation sets.
- **Add the two sections of `method/sdd-addendum.md`** right after `## Section 4: Integrations` and before the template's later sections, headings exactly as written: the claim entity with its write-ownership matrix, and *Design Feedback to PDD*.
- **The gate**: `python3 1-design/check_sdd.py sdd.md --pdd PDD.md`. One command runs the planner's shape audit, then checks the design against the process: task types against the PDD, one writer per column, every read variable produced, real argument names, tables that render. It must exit 0. A rule you believe is wrong: say so in `PROGRESS.md` and a finding, and leave the document as it is.

## What bites

| Issue | Fix |
|---|---|
| Two conditions share a display name — *Stage started* on six tasks | Condition names are one pool across the whole case: stage entry, stage exit, task entry, case exit. The planner's audit does not check it; `uip maestro case validate` refuses it at `3d`. Name each for what it tests. |
| `validate --strict --sdd` rejects the task-output variables listed in *Case Variables*, and `check_sdd.py` BIND-7 fails when they are missing | List them in the one `### Case Variables` table, with the other variables — `sdd convert` reads only the first table there and drops a second one silently. Write each output row as a plain `Field -> outX`, nothing after it. |

**Put every routing conclusion in a case condition over facts an Agent reports** — the aggregate bound the settlement, the settlement adds up, the claimant's account rules out its own cause (`3c-agents/cookbook.md`, *An Agent whose verdict routes a claim reports facts*). A conclusion left to a prompt is the one Verify spends its cycles on. **The same goes for arithmetic:** a sum, a cap, a net payable or a ratio the case can compute from figures an Agent reports is a case expression over integer cents, never an Agent output that has to repeat exact digits.

**Gate tasks and SLA notifications go to the seat owner** (`User:` with your sign-in email), never to a group — `contracts/review-task.md`, *Who receives it*.

## Reading the checker

`FAIL` reaches the built plan · `WARN` is worth a look and does not stop a build · `NOTE` is something it could not decide, which is never a pass.

**Read three rules before writing** — they shape how the document is written: `HANDOFF-3` (no SME item left `Blocking = yes`), `ACT-1` (how a gateway's task block names its Action output), `OWN-1` (the write-ownership matrix and the entity table name the same writers).

**Three ways a design passes both gates and still cannot be built:** `ARG-1` — an `rpa` task bound to an argument the automation does not have; read arguments from `uip or packages entry-points`, never from memory. `JS-1` — a helper in an `=js:` expression that nothing defines (`nowIso()`); the grammar has none, write it inline. `ACT-2` — a gateway whose outputs never map the platform's literal `Action`.

`NATURE-3` lists tasks it could not match to a PDD step; until it is zero, their types were not checked.
