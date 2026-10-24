# The case — what bites

`check_caseplan.py` catches what it names — undeclared `vars.`, output names without `out_`, connector inputs without `target`, payloads no write carries, missing layout entries, backticks `sdd convert` carried into a value, conditioned tasks sharing a task set, two entry conditions on one task. `validate --strict --sdd sdd.md` catches what differs from the design. This page covers what neither catches.

| Issue | Fix |
|---|---|
| An Orchestrator automation typed `process` does not resolve | Type it **`rpa`**. `process` resolves against `processOrchestration-index.json`, which is empty on this tenant; the six provided automations are in `process-index.json`. The planner types them `process`, so correct the SDD (`check_sdd.py` `TYPE-4`). |
| A timer converts empty, or `validate` rejects its duration | A timer takes a literal ISO 8601 duration (`PT2M`) — `validate` refuses `=vars.…` and `=js:…` there. Write the SDD's `**Timer:**` cell as the bare duration; convert copies it, and the template's `timeDuration (relative)` gloss left beside it converts to an empty timer. |
| A value in the converted plan reads as its own expression text | `sdd convert` keeps the SDD's backticks on some values (`` "`=js:…`" ``), and the runtime then stores that text. Remove the backticks in `caseplan.case` after every convert — the SDD is right to have them. `check_caseplan.py` lists each one as `BACKTICKED`. |
| `validate --strict` warns `ASSIGNMENT_NOT_ALLOWED` inside an expression's function | A local variable assigned inside an `=js:` expression's own function (`(() => { let t = …; return …; })()`) is flagged and runs correctly. Leave it, or inline the value. |
| `registry search` does not find the Action App you just deployed | A plain `registry pull` keeps the cached `action-apps` list: `uip maestro case registry pull --force`, then `search <app> --type action-apps`. |
| An `app` entry appears under `resources/solution_folder/` | `resources refresh`, `solution pack` and `solution upload` re-create it from the app entry in the case's `bindings_v2.json`, and `uip maestro case bindings sync` writes that entry back on every run. Remove the resource (`uip solution resources remove <app id> --solution-folder <dir>`) and drop the app entry from `bindings_v2.json` after every `bindings sync`. The caseplan's root binding is what the runtime uses (`CONFIG.md`, *Deploying*). |

## The whole claim faults at case start, before anything runs

Every entry, exit and completion condition is evaluated once when the case starts, while every variable is still empty. An unguarded JSON parse or property read throws at that point and faults the whole claim, on a node that appears nowhere in your plan. Guard every parse (`|| '{}'`) and every property read (`?.`). **The same parse faults mid-run on an Agent's invalid output** — after a human has already decided — so wrap every `JSON.parse` of Agent output in `try`/`catch` and let unreadable count as flagged.

## Structure

| Issue | Fix |
|---|---|
| A clean claim still raises a human gate, or a skipped gate strands the task after it | **A `skipCondition` does not stop a human gate being raised**: the Action Center task is created before the skip is evaluated. Make the gate **`Required: No`** and put the inverted test on its **entry condition**: `=js:String(vars.allChecksPassed).toLowerCase() !== "true"`. Give the task after the gate its own way to start: a second DNF group in its one entry condition, `selected-tasks-completed` on the gate's predecessor with `=== "true"`. The `String(...)` matters because a boolean case variable reaches a condition as the string `'true'`, and unset, empty and false must all open the gate (`PDD.md` §5.7). Both gate booleans default to `false`. |
| Every claim faults at the first file read (`400300 Failed to evaluate expression: =out_ClaimFormPDF`), or the file's case variable holds a JSON schema and the next Agent rejects it (`AGENT_STARTUP.INPUT_VALIDATION_ERROR`) | A `file` output is **one entry**: `type: file`, `target: =orchestrator.JobAttachments`, `var` = the case variable, **no `body`**. Convert writes `target: "=<id>"`, which faults; a `body` on that entry is compiled in and the variable then holds the schema. `validate --strict` accepts all three. Compare each output row with `uip maestro case tasks describe` for its task; `check_caseplan.py` reports `FILE TARGET` and `FILE BODY`. |
| `decisionReason` says *Approve* on a refused claim | Take the human's word first: the override's `outcomeLabel`, else `reviewDecision` when a human decided, else the recommendation. |
| A lane is entered on a gate decision, and the origin's happy path runs as well | The lane's entry and the origin's completion fire from the same event, so pair them. Either guard the lane's entry and the next primary stage's entry with exact-inverse tests, or give the origin a diverting exit to the lane. Two entries that can both be true run a stage twice. |
| The claim record is written five times in one stage | **One write per stage**, as its last required task. A stage that holds a human gate gets two: one before the gate opens and one after it closes. Adjacent writes with no gate between them count as one write. After parallel producers, the write is a single `selected-tasks-completed` fan-in that names all of them. |

## Output rows that pass strict and run

Write these shapes in `sdd.md`, so convert emits them and `validate --strict --sdd` holds the plan to them:

| Issue | Fix |
|---|---|
| The `--sdd` audit does not see a task's outputs | Head the table `**Outputs:**` — the audit reads only that label, although convert also reads `**Output Schema:**`. |
| A computed output is missing from the plan | Write it as its own row, `\| — \| name = expr \|`, under `**Outputs:**`. |
| An expression check passes because it never saw the expression | Backtick every `=js:` in the SDD (`check_sdd.py` `JS-0`); strip the backticks convert keeps in `caseplan.case` (`BACKTICKED`). |
| `STRICT_OUTPUT_SELF_REFERENCE`, or a row reads a value its own task has not written yet | An output may not read the variable it writes, and a row that reads a name a later row of the same task writes gets the default. Copy the raw value first — a helper row on the producer task, `rawName = expr` — then derive from the helper on the task that needs it. Rows run in table order. |

## Canvas

**Place every stage yourself.** `sdd convert` writes no layout and the skill's Rule 19 says to emit `layout: {}`, but that auto-arranges the stages into a grid that does not read as the process. A layout map that lists some nodes but not all crashes the designer on load, and `check_caseplan.py` reports that case. Follow this page, not the skill:

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

**Nothing overlaps.** A card grows about 45 px per task on a 230 px header, so the second row starts below the tallest card of the first row: around `y = 700` when Intake has eight tasks. Coordinates for eight stages: first row `y = 220`, `x = 220, 580, 940, 1300, 1660` (a card is about 304 px wide, so step at least 360); Denied `x = 1660, y = 620`; second row `y = 700`, Missing details `x = 220`, Awaiting inspection `x = 580`. The relationships matter, not these exact numbers.

## Writing to a folder-scoped entity: use the V3 activities

Your claim entity is folder-scoped, and **the Data Fabric connector's default (V2) activities resolve entity names at tenant level only**. A write generated the ordinary way packs, validates and deploys, then faults on the first row with `[102003] Entity 'ClaimCase_<seat>' not found at tenant level`. **That error does not mean folder scope is unreachable.** Three different mistakes return the same *entity does not exist*:

| What you did | What you get back |
|---|---|
| used the **V2** activity | `not found at tenant level` |
| used V3 with **PascalCase** query keys | `404 Entity … does not exist` |
| used V3 with `folderEntityNameFolderPath` (the underscore lost) | `404 Entity … does not exist` |
| used V3 with a companion name the connector no longer knows (`_folderPath` after it became `_folderKey`) | `not found at tenant level`, on every claim, with nothing in your build changed |
| used V3 correctly | the row |

**Generate these writes, and ask for the V3 objects by name:**

```bash
uip maestro case spec --type activity --activity-type-id <id> \
  --connection-id <your-connection> --object-name CreateEntityRecord_V3 \
  --input-details '{"queryParameters":{"entityScope":"folder",
                    "folderEntityName":"ClaimCase_<seat>",
                    "folderEntityName_folderKey":"<your seat folder key>",
                    "folderEntityName_folderPath":"ClaimCase-<seat>"}}'
```

- **The query keys are lower case, with an underscore in the folder companion.** Every parameter is a query parameter. `pathParameters` stays `{}`; there is no `entityName` parameter.
- **These V3 objects are `PREVIEW`, and the companion has already been renamed once**: `folderEntityName_folderPath` (the folder's path) became `folderEntityName_folderKey` (the folder's GUID). The connector ignores a name it no longer knows instead of refusing it, so the write loses its folder and fails as *not found at tenant level*. Take every spelling from `uip is resources describe uipath-uipath-dataservice CreateEntityRecord_V3 --operation Create` **on the day you build**, and **send both names**: the spare costs nothing and survives the next rename.
- **The update operation is `Replace`, not `Update`.** `uip is resources describe uipath-uipath-dataservice UpdateEntityRecord_V3 --operation Update` answers *Operation 'Update' not found. Available: Replace* (`PUT /v3/UpdateEntityRecord/update`). It requires `entityScope` and `recordId` as query parameters, plus the same companion pair as the create. Despite the name, it still patches the record the way `contracts/claim-entity.md` describes.
- **The create returns the row id as `Id`.** Write the SDD's output row as `response.Id -> recordId`; a bare `Id -> recordId` makes `validate --strict --sdd` demand `source "=Id"`. The build renders it as `source: =response.Id`, and every later write passes it as its `recordId` query parameter.

## What only a run shows

| Issue | Fix |
|---|---|
| A task starts alongside the task it should follow, or starts twice | **`runs-sequentially` orders chain members, not tasks.** A task joins the chain only when `runs-sequentially` is the sole rule of its sole entry condition, and it waits for the previous chain member. So after a `current-stage-entered` task it starts at once; after a two-task group it can start once per predecessor; and a task taken out of the chain hands its successor the task set before it. The skill and the planner both prescribe these chains, including `[[A],[B,C],[D]]`, which double-starts D under load. In a stage with a parallel group or a fan-in, use no `runs-sequentially` at all: every task after the first names the tasks it waits for with `selected-tasks-completed`. Change it in the SDD first, because the strict audit holds the plan to the SDD. Both validators pass every variant. |
| Tasks start on stage entry although each has its own entry condition | Tasks that share one task set (one inner array of `data.tasks`) **lose their own `entryConditions` in the compiled `caseplan.case.bpmn`** — their rule ids are absent, so they start with the stage. Give every task that carries a condition its own task set; siblings that name the same predecessor in `selected-tasks-completed` still start in parallel. Grep the compiled file for each rule id. Both validators pass the shared set, and convert writes it for tasks the SDD lists together. |
| Two `entryConditions` on one element, meant as alternatives | They are **ANDed**. Alternatives are DNF groups inside one condition, but the skill's *one row = one condition object* rule builds the AND, and convert does the same for two Entry Condition rows. Merge them into one condition with one group per row. |
| A follow-up lane re-enters a stage and the claim sits `InProgress` for ever | An entry condition cannot re-enter a stage that never left. If the origin stage is still `InProgress` when the lane fires, both stay open and nothing reports an error. Make the origin exit before the lane's entry fires, or keep the poll inside the stage (an `rpa` task re-entered on a timer). |
