# Plan

You have a design that says what the solution is. Turn it into the order things get built in.

Use **`uipath-planner`** again to derive the task list from `sdd.md` into `tasks.md` at the folder's root: what gets built, in what order, by which skill, and where you stop to check.

Guidelines:
- Nothing binds to something unbuilt. Whatever is referenced by name comes first: the models, the automations, the claim entity, the solution the case and the Agents live in, the review app.
- The review app's contract comes before the case, because the case binds it; its screens come after a run.
- Route, don't redescribe. Each task names its skill and the parts of `sdd.md` to read; the list never re-explains the architecture.
- The case is one task. Its stages, tasks and conditions are in `sdd.md`, not here.
- Every task that generates something has a check, and testing comes before anything deploys.

**Done when:**
- someone could work the list top to bottom without opening the design to find out what comes next
- nothing in it is blocked by something further down.
