# The case — what bites

**Run `check_caseplan.py` before you run the case.** Everything below that it can detect, it detects.

| Issue | Fix |
|---|---|
| An optional value arrives as `""` and destroys what an earlier stage wrote | **An empty string is not an empty value.** An unset case variable resolves to `""`, and a write of `""` erases. Coalesce to omitted. |
| `response.X` returns nothing | It belongs to **connector tasks only**. On any other task type it resolves to nothing, silently. |
| A payload is produced and nothing ever reads it | A payload with no write task is data that vanishes. Every one needs a destination or a deliberate note that it has none. |
| An output binds by a name you chose | **Outputs keep their `out_` prefix.** The name is the component's, not yours. |
| A connector input is ignored | Connector inputs use `target` + `body`, **never `value`**. |
| A human gate's answer never arrives | The outcome binds as a task output literally named **`Action`**, capital A. Not `outcome`, and no cross-reference. |
| An Orchestrator automation will not resolve | Its task type is **`rpa`**, not `process`: `process` resolves against `processOrchestration-index.json`, which is empty on this tenant; `rpa` resolves against `process-index.json`, where all six provided automations live. The planner types them `process`; correct the SDD (`check_sdd.py` warns, `TYPE-4`). |
| Writes to your record fail with *entity not found at tenant level* | A folder-scoped record needs the **V3** connector activities, not the V2 ones the tooling reaches for by default — *Writing to a folder-scoped entity*, below. **Do not conclude the entity is unreachable**: three different mistakes give that same 404. |

## The whole claim faults at case start, before anything runs

**Every entry, exit and completion condition is evaluated once when the case starts**, when all variables are still empty. A condition that parses a JSON column then sees `null`, and the read that follows throws — faulting the claim with an error naming a node that appears nowhere in your design.

Guard every parse (`|| '{}'`) and every property read (`?.`). This is the single most expensive shape in the whole build, because the error points at nothing you wrote.

## Structure

| Issue | Fix |
|---|---|
| Three tasks that should run together run one after another | **Parallelism is expressed by grouping, not by ordering.** Sequencing them does not make them concurrent. |
| A skipped human gate leaves the claim waiting forever | **Whatever runs after a gate needs its own way to start.** A gate that never opens starts nothing. |
| A clean claim stops anyway, or a flagged one sails through | **A `skipCondition` does not stop a human gate being raised**: the platform instantiated the Action Center task before evaluating the skip, so a clean claim got a row. The shape that works: the gate task is **`Required: No`**, its **entry condition** carries the inverted test — `=js:String(vars.allChecksPassed).toLowerCase() !== "true"` — and the task after the gate gets a **second entry condition**, `selected-tasks-completed` on the gate's predecessor gated on `=== "true"`, so the clean path has its own way to start. Two reasons for the `String(...)` form: a boolean case variable arrives at a condition as the string `'true'`, so a bare `=== true` is false even when the value is genuinely true; and unset, empty and false must all **open** the gate — `PDD.md` §5.7 fails towards the human. Both gate booleans carry `Default: false`. |
| A file an `rpa` task returned never reaches its case variable — the consumer receives a JSON *schema* instead | An `rpa` task's file output needs **two output entries** for the same output name: the one `tasks describe` gives you (`type: file`, `target: =orchestrator.JobAttachments`) **and** an ordinary extraction (`type: jsonSchema`, `id`/`var`/`value` = the case variable, `target: =<var>`, no `body`). One alone leaves the variable unset, and an unset file variable reads back as its declared schema, PascalCased, which fails the consumer's input validation on a missing `ID`. `validate` accepts every wrong variant. |
| The first gate faults *No app: claim-review-<seat> found in folder:* with an empty folder name | The app's `folderPath` binding must be explicit — the seat folder where the standalone app is deployed (`CONFIG.md`, *Deploying*). The seven Agents resolve with an empty default; an app does not. Change only the caseplan binding's default — not the case project's `bindings_v2.json`, which forks a second app resource and refuses the next deploy with `4010`. |
| `validate` says *Variable 'vars.scenario' does not exist* for an input you declared | A case **input** is not shaped like a case output. Inputs take the `inputOutputs` shape — `{id, name, type, custom: true, elementId: 'root', default}` with `id` equal to the name — not the `{id, name, type, var}` shape of `variables.outputs`. Declare `scenario`, `discrepancy`, `profileId` and `seed` as inputs, or every run draws a random claim and no run can be aimed or repeated. |
| `decisionReason` says *Approve — decided by a claims adjuster* on a refused claim | The expression fell through the override's `outcomeLabel` to the agent's `recommendedOutcome` and never consulted the human. Prefer `outcomeLabel`, else the human's `reviewDecision` when one exists, else the recommendation — the audit line's one load-bearing word is the human's. |
| A stage is entered twice | Two entry conditions that can both be true at once is a double execution waiting to happen. Mutually exclusive is fine. |
| The case never completes | A stage exits on a condition, and a condition nothing can satisfy is a dead case. Every exit needs something that can make it true. |
| The Action App says *not available yet* while the case runs perfectly | The app renders what has been **written** to the Data Fabric record. A write that feeds a human step must sit **before** it. |
| The Data Fabric record is written five times in one stage | Budget **one write per stage**, two where a stage has a human gate. Two adjacent writes are one write. |

## The edit does not take effect

**`caseplan.json` is not what runs.** The compiled `caseplan.json.bpmn` beside it is. Before believing any edit landed, grep the compiled file for a token that exists nowhere else — this produced three contradictory conclusions in one afternoon before the mechanism was understood.

**Only one command compiles it, and it is not the one you will reach for.**

| Command | What it does to `caseplan.json.bpmn` |
|---|---|
| `uip maestro case pack <project> <out>` | **Compiles it**, wrapper and all. This is the one. |
| `uip solution pack` | **Copies what is beside `caseplan.json`; never regenerates it.** On 1.199 it omitted the file entirely; on 1.201.0-preview.127 it packed both `caseplan.json` and `caseplan.json.bpmn` — either way the compiled file exists only if `case pack` ran first |
| `uip maestro case validate` | Does not generate it. A plan can be `Valid` and unpackageable |

Deploy a solution packed without it and the job faults at run time with *"entry point could not be resolved to a BPMN file"* — nothing fails at pack time. **Case-pack first, then solution-pack**, and check the compiled file is in the package before you deploy.

`uip maestro case validate` may or may not accept your plan's schema version — check once, then pin whichever works.

## Canvas

**Do not author edges** — they are retired, and hand-written ones are ignored or worse. **Place the stages yourself**: a stage with no layout entry crashes the designer outright, with an error naming nothing that appears in the plan.

> **This contradicts the `uipath-maestro-case` skill, which says to emit `layout: {}` and never a position** on the grounds that the canvas auto-arranges. **Follow this page.** The skill's rule is about not wasting tokens on fields the frontend strips; ours is about a designer that will not open. A crash outranks a token count, and you will find out which is right the moment you try to look at your plan.

**Placing them is not decoration.** Edges are gone, so position is the only thing left that shows a reader how the claim moves — and the case diagram is the first picture anyone sees of the whole process, including people who will never read the plan. This is the picture:

```
    ┌────────┐   ┌───────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 ●─▶│ Intake │──▶│ Screening │──▶│ Analysis │──▶│  Review  │──▶│ Approved │
    └────────┘   └───────────┘   └──────────┘   └──────────┘   └──────────┘
         │             │                                       ┌──────────┐
         ▼             ▼                                       │  Denied  │
    ┌───────────┐ ┌───────────┐                                └──────────┘
    │  Missing  │ │ Awaiting  │
    │  details  │ │inspection │
    └───────────┘ └───────────┘
```

| Rule | Why |
|---|---|
| **The decision path runs left to right on one row** — Intake · Eligibility screening · Analysis · Claim review · Approved | it is the shape a business reader already has in their head |
| **Denied sits directly below Approved**, on the right | an ending is where the eye stops; the common outcome is the one on the natural line |
| **Missing details sits below Intake; Awaiting inspection sits below Eligibility screening** | each drops out of the stage it follows, which is the one thing edges used to say. Awaiting inspection stays a **primary** stage — every claim passes through it and a secondary stage can never be required for completion — its position is the only thing that changes |
| **Nothing overlaps.** A stage card grows with its tasks (roughly 45 px per task on a 230 px header), so the second row starts **below the tallest card of the first** — with eight tasks in Intake that is around `y = 700`, not one nominal row-height down | a lane drawn into another card reads as part of it |

Coordinates that give this picture, for eight stages: first row `y = 220`, `x = 220, 520, 820, 1120, 1420`; Denied `x = 1420, y = 620`; second row `y = 700`, Missing details `x = 220`, Awaiting inspection `x = 520`. **Even spacing and the relationships are what matter, not these numbers** — and every stage needs a `layout.nodes` entry or the designer will not open.

## Writing to a folder-scoped entity: use the V3 activities

Your claim entity lives in your seat folder (`CONFIG.md`) and **the Data Fabric connector's default activities resolve entity names at tenant level only.** Generate the write the ordinary way and the case packs, validates and deploys cleanly, then faults on the first row with `[102003] Entity 'ClaimCase_<seat>' not found at tenant level`.

**A 404 here does not mean folder scope is unreachable.** It is reachable — proven at run time, rows created and updated across five stages. Three separate mistakes produce an identical *entity does not exist*, and only by ruling out all three do you learn anything:

| What you did | What you get back |
|---|---|
| used the **V2** activity | `not found at tenant level` |
| used V3 with **PascalCase** query keys | `404 Entity … does not exist` |
| used V3 with `folderEntityNameFolderPath` (the underscore lost) | `404 Entity … does not exist` |
| used V3 correctly | the row |

**Do not hand-author these — generate them**, asking for the V3 objects by name. The type cache advertises only V2 and `spec` builds them anyway:

```bash
uip maestro case spec --type activity --activity-type-id <id> \
  --connection-id <your-connection> --object-name CreateEntityRecord_V3 \
  --input-details '{"queryParameters":{"entityScope":"folder",
                    "folderEntityName":"ClaimCase_<seat>",
                    "folderEntityName_folderPath":"ClaimCase-<seat>"}}'
```

Three details, each worth a deploy cycle:

- **The query keys are lower-case, with an underscore in `folderEntityName_folderPath`** — and `case spec` prints them PascalCased with the underscore dropped (`known-issues/cli-commands.md`). Take every spelling from `uip is resources describe uipath-uipath-dataservice CreateEntityRecord_V3 --operation Create`, never from `spec`.
- **There is no `entityName` path parameter** — every parameter is a query parameter and `pathParameters` stays empty. Connector inputs use `target` + `body`, never `value`; get that wrong and the query parameters are never dispatched, and it reports as a *missing path variable* naming its own URL template.

**The update operation is `Replace`, not `Update`** — the name everyone types first. `uip is resources describe uipath-uipath-dataservice UpdateEntityRecord_V3 --operation Update` answers *Operation 'Update' not found. Available: Replace* (`PUT /v3/UpdateEntityRecord/update`; required `entityScope` and `recordId`, both query parameters, plus the same `folderEntityName` / `folderEntityName_folderPath` pair as the create). The name notwithstanding, the write is still the patch `contracts/claim-entity.md` describes — omitted fields survive, `null` and `""` destroy.

**The row id comes back on the create's response as `Id`.** Bind it once — `Id -> recordId`, which the build renders as `=response.Id` — and every later write passes it as its `recordId` query parameter. The v1 reference did exactly this; it is the single most load-bearing binding in the plan, so confirm it survives `case spec` before anything else is generated.

**`uip df records insert --folder-key` writing fine proves nothing about the connector** — a different client with different scoping. The entity looks healthy right up until the case tries to write it.

## What only a run shows

| Issue | Fix |
|---|---|
| The second task of a stage starts alongside the first | **`runs-sequentially` is chain-position magic, not an ordering.** A task marked `runs-sequentially` after a task with a `current-stage-entered` entry is a parallel start. Remove `runs-sequentially` from the plan entirely and gate every later task with `selected-tasks-completed` plus an explicit `selectedTasksIds` naming the task it waits for. Both design gates pass either way. |
| Two `entryConditions` on one element, meant as alternatives | They are **ANDed**. Alternatives are DNF groups inside ONE condition. A clean claim can pass by accident when both happen to be true, which is how it hides. |
| A follow-up lane re-enters a stage and the claim sits `InProgress` for ever | An entry condition cannot re-enter a stage that never left: if the origin stage is still `InProgress` when the lane fires, both stay open and nothing errors — a poll lane keyed on `selected-stage-exited` stalls a share of claims silently. Make the origin stage exit before the lane's entry, or keep the poll inside the stage (an `rpa` task re-entered on a timer). Prove whichever you choose on several clean claims before `4-verify`. |
| An agent task faults with an empty `end_execution` | Not a business outcome. `uip maestro case instance retry` recovers it in place; a fault handler that reads it as "no findings" settles a claim nobody analysed. |
| `uip solution resources refresh` wrote an `app` entry under `resources/solution_folder/` | Delete it before you pack, every time. The app is external — bound by name and the seat folder's path, never provisioned by the solution. A provisioned copy shares the standalone app's model; once that app is upgraded, every solution redeploy fails `FailedInstall` on it and the only way through is unpacking the zip by hand. |