# Plan

You have a design that says what the solution is. Turn it into the order things get built in.

Use **`uipath-planner`** again and derive the implementation task list from `sdd.md` into `tasks.md` — that name, at this folder's root, whatever the design's handoff header proposes. This says what gets built, in what order, by which skill, and where you stop to check. It is consumed during the build and then done with — and **each block sets the `Status:` line of the tasks it finishes**, not only the sub-items: a later reader scans the status line, nothing makes the two agree, and on one build 14 of 28 statuses read *pending* for work finished days earlier.

- **Leaves before consumers.** Anything referenced by name has to exist and be published first — models, workflows, processes used as tools, the claim entity, the solution the case and the Agents are scaffolded inside, the standalone Action App deployed into the seat folder. Nothing binds to something unbuilt. The least obvious leaf is the Action app's *contract* (`contracts/review-task.md`): the case binds it, so it is registered — empty page and all — before the case, and the screens come after a run.
- **Routing, not redescription.** Each task names which skill builds it and which `sdd.md` sections to read. It does not re-explain the architecture; that drifts, and then two documents disagree.
- **A `Validate:` step on every task that generates something**, and a testing task before anything deploys.

**Done when someone could work the list top to bottom without opening the design to find out what comes next** — and when nothing in it is blocked by something further down.
