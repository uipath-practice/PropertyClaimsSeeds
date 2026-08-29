# Plan

You have a design that says what the solution is. Turn it into the order things get built in.

Use **`uipath-planner`** again and derive the implementation task list from `sdd.md` into `tasks.md`, which says what gets built, in what order, by which skill, and where you stop to check. Store it at the folder's root; it is consumed during the build.

- Anything referenced by name has to exist and be published first: models, workflows, processes used as tools, the claim entity, the solution the case and the Agents are scaffolded inside, the standalone Action App deployed into the seat folder. Nothing binds to something unbuilt. 
- Action App's *contract* (`contracts/review-task.md`): the case binds it, so it is registered before the case, and the screens come after a run. 
- Routing, not redescription. Each task names which skill builds it and which `sdd.md` sections to read. 
- Tasks document does not re-explain the architecture; that drifts, and then two documents disagree.
- A `Validate:` step on every task that generates something, and a testing task before anything deploys.
- Each later block sets the `Status:` line of the tasks it finishes, not only the sub-items — the status line is what a reader scans.

**Done when:**
- someone could work the list top to bottom without opening the design to find out what comes next
- nothing in it is blocked by something further down.
