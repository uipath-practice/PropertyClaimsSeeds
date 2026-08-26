# The case — what bites

**Run `check_caseplan.py` before you run the case.** Everything below that it can detect, it detects.

## Bindings that resolve to nothing

Four shapes pass every gate and bind to nothing at run time.

| Issue | Fix |
|---|---|
| An optional value arrives as `""` and destroys what an earlier stage wrote | **An empty string is not an empty value.** An unset case variable resolves to `""`, and a write of `""` erases. Coalesce to omitted. |
| `response.X` returns nothing | It belongs to **connector tasks only**. On any other task type it resolves to nothing, silently. |
| A payload is produced and nothing ever reads it | A payload with no write task is data that vanishes. Every one needs a destination or a deliberate note that it has none. |
| An output binds by a name you chose | **Outputs keep their `out_` prefix.** The name is the component's, not yours. |
| A connector input is ignored | Connector inputs use `target` + `body`, **never `value`**. |
| A human gate's answer never arrives | The outcome binds as a task output literally named **`Action`**, capital A. Not `outcome`, and no cross-reference. |
| An Orchestrator automation will not resolve | Its task type is **`rpa`**, not `process`. |
| Writes to your record fail with *entity not found at tenant level* | A folder-scoped record needs the **V3** connector activities, not the V2 ones the tooling reaches for by default — *Writing to a folder-scoped entity*, below. **Do not conclude the entity is unreachable**: three different mistakes give that same 404. |

## The whole claim faults at case start, before anything runs

**Every entry, exit and completion condition is evaluated once when the case starts**, when all variables are still empty. A condition that parses a JSON column then sees `null`, and the read that follows throws — faulting the claim with an error naming a node that appears nowhere in your design.

Guard every parse (`|| '{}'`) and every property read (`?.`). This is the single most expensive shape in the whole build, because the error points at nothing you wrote.

## Structure

| Issue | Fix |
|---|---|
| Three tasks that should run together run one after another | **Parallelism is expressed by grouping, not by ordering.** Sequencing them does not make them concurrent. |
| A skipped human gate leaves the claim waiting forever | **Whatever runs after a gate needs its own way to start.** A gate that never opens starts nothing. |
| A clean claim stops anyway, or a flagged one sails through | The skip test is `!== false`, **never `=== true`**, and there are two independent reasons. Fail *towards* the human, so "not yet written" must not read as "flagged" — and **a boolean case variable arrives at a condition as the string `'true'`**, so `=== true` is false even when the value is genuinely true. Measured: a component returned a real JSON `true`, the variable was declared `boolean`, the record showed `True`, and **both human gates were unreachable** — every part of it looking correct. |
| A stage is entered twice | Two entry conditions that can both be true at once is a double execution waiting to happen. Mutually exclusive is fine. |
| The case never completes | A stage exits on a condition, and a condition nothing can satisfy is a dead case. Every exit needs something that can make it true. |
| A validation app says *not available yet* while the case runs perfectly | The screen is built from what has been **written**. A write that feeds a human step must sit **before** it. |
| The record is written five times in one stage | Budget **one write per stage**, two where a stage has a human gate. Two adjacent writes are one write. |

## The edit does not take effect

**`caseplan.json` is not what runs.** The compiled `caseplan.json.bpmn` beside it is. Before believing any edit landed, grep the compiled file for a token that exists nowhere else — this produced three contradictory conclusions in one afternoon before the mechanism was understood.

**Only one command compiles it, and it is not the one you will reach for.**

| Command | What it does to `caseplan.json.bpmn` |
|---|---|
| `uip maestro case pack <project> <out>` | **Compiles it**, wrapper and all. This is the one. |
| `uip solution pack` | **Omits it from the package entirely** — even though `package-descriptor.json` lists it |
| `uip maestro case validate` | Does not generate it. A plan can be `Valid` and unpackageable |

Deploy a solution packed without it and the job faults at run time with *"entry point could not be resolved to a BPMN file"* — nothing fails at pack time. **Case-pack first, then solution-pack**, and check the compiled file is in the package before you deploy.

`uip maestro case validate` may or may not accept your plan's schema version — check once, then pin whichever works.

## Canvas

**Do not author edges** — they are retired, and hand-written ones are ignored or worse. **Place the stages yourself**: a stage with no layout entry crashes the designer outright, with an error naming nothing that appears in the plan.

> **This contradicts the `uipath-maestro-case` skill, which says to emit `layout: {}` and never a position** on the grounds that the canvas auto-arranges. **Follow this page.** The skill's rule is about not wasting tokens on fields the frontend strips; ours is about a designer that will not open. A crash outranks a token count, and you will find out which is right the moment you try to look at your plan.

**Placing them is not decoration.** Edges are gone, so position is the only thing left that shows a reader how the claim moves — and the case diagram is the first picture anyone sees of the whole process, including people who will never read the plan. Three rules, and they cost nothing at authoring time:

```
    ┌────────┐   ┌───────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 ●─▶│ Intake │──▶│ Screening │──▶│ Awaiting │──▶│ Analysis │──▶│  Review  │──┐
    └────────┘   └───────────┘   └──────────┘   └──────────┘   └──────────┘  │
                       │                                                     │
                       ▼                                    ┌──────────┐ ◀───┤
                 ┌───────────┐                              │ Approved │     │
                 │  Missing  │   ← secondary lane sits      └──────────┘     │
                 │  details  │     under the stage it       ┌──────────┐ ◀───┘
                 └───────────┘     branches from            │  Denied  │
                                                            └──────────┘
```

| Rule | Why |
|---|---|
| **The happy path runs left to right, on one row, in lifecycle order** | it is the shape a business reader already has in their head; anything else makes them work out the order from the labels |
| **Terminal stages go furthest right, stacked** | an ending is where the eye stops. Approved above Denied, so the common outcome is the one on the natural line |
| **A secondary lane sits directly below the stage it branches from** | its position then *says* where it came from, which is the one thing edges used to say and no longer can |

**Coordinates are yours**; even spacing on the primary row and one row-height down for a lane is enough. What matters is the relationship, not the numbers.

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

- **The query keys are lower-case**, and `case spec` prints them PascalCased like everything else this CLI displays. Lower-case them on the way in.
- **One of them cannot be fixed by lower-casing.** `spec` drops the underscore too, so `folderEntityName_folderPath` comes back as `FolderEntityNameFolderPath` → `folderEntityNameFolderPath`, which is not a parameter name. **Take the real spelling from `uip is resources describe uipath-uipath-dataservice CreateEntityRecord_V3 --operation Create`**, never from what `spec` echoed.
- **There is no `entityName` path parameter** — every parameter is a query parameter and `pathParameters` stays empty. Connector inputs use `target` + `body`, never `value`; get that wrong and the query parameters are never dispatched, and it reports as a *missing path variable* naming its own URL template.

**`uip df records insert --folder-key` writing fine proves nothing about the connector** — a different client with different scoping. The entity looks healthy right up until the case tries to write it.
