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
| Writes to your record fail with *entity not found at tenant level* | A folder-scoped record needs the **V3** connector activities, not the V2 ones the tooling reaches for by default. Six lines of difference and it is the whole failure. |

## The whole claim faults at case start, before anything runs

**Every entry, exit and completion condition is evaluated once when the case starts**, when all variables are still empty. A condition that parses a JSON column then sees `null`, and the read that follows throws — faulting the claim with an error naming a node that appears nowhere in your design.

Guard every parse (`|| '{}'`) and every property read (`?.`). This is the single most expensive shape in the whole build, because the error points at nothing you wrote.

## Structure

| Issue | Fix |
|---|---|
| Three tasks that should run together run one after another | **Parallelism is expressed by grouping, not by ordering.** Sequencing them does not make them concurrent. |
| A skipped human gate leaves the claim waiting forever | **Whatever runs after a gate needs its own way to start.** A gate that never opens starts nothing. |
| A clean claim stops anyway | The skip test is `!== false`, **never `=== true`** — fail *towards* the human, but do not treat "not yet written" as "flagged". |
| A stage is entered twice | Two entry conditions that can both be true at once is a double execution waiting to happen. Mutually exclusive is fine. |
| The case never completes | A stage exits on a condition, and a condition nothing can satisfy is a dead case. Every exit needs something that can make it true. |
| A validation app says *not available yet* while the case runs perfectly | The screen is built from what has been **written**. A write that feeds a human step must sit **before** it. |
| The record is written five times in one stage | Budget **one write per stage**, two where a stage has a human gate. Two adjacent writes are one write. |

## The edit does not take effect

**`caseplan.json` is not what runs.** The compiled artifact beside it is, and packing copies rather than compiles. Before believing any edit landed, grep the compiled file for a token that exists nowhere else. This produced three contradictory conclusions in one afternoon before the mechanism was understood.

`uip maestro case validate` may or may not accept your plan's schema version — check once, then pin whichever works.

## Canvas

**Do not author edges** — they are retired, and hand-written ones are ignored or worse. **Place the stages yourself**: a stage with no layout entry crashes the designer outright, with an error naming nothing that appears in the plan.

## Deploying

| Issue | Fix |
|---|---|
| A redeploy creates a second deployment | Same name, every time — `CONFIG.md`, *Deploying*. |
| `Validation failed` on a deploy that never got that far | It is a **failed uninstall** reported as a validation error. Clear the half-failed deployment first. |
| A bound automation is not found, five seconds in, having executed nothing | The folder. `contracts/provided-processes.md`, last section. |

## When a claim does not do what you expected

Read the instance, not the job list. The variable table at run time is what the case actually had; the incident detail is long and **the cause is at the end**, not the start.
