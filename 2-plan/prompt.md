# Plan

You have a design. Turn it into the order things get built in.

Use **`uipath-planner`** and derive the implementation task list from `sdd.md` into `tasks.md`. **A different skill from `1-design`'s, doing a different job:** the design says what the solution is, this says what gets built, in what order, by which skill, and where you stop to check. It is consumed during the build and then done with.

What makes this worth its own step rather than something you improvise later:

- **Leaves before consumers.** Anything referenced by name has to exist and be published first — models, workflows, processes used as tools, the claim entity. Nothing binds to something unbuilt.
- **Routing, not redescription.** Each task names which skill builds it and which `sdd.md` sections to read. It does not re-explain the architecture; that drifts, and then two documents disagree.
- **A `Validate:` step on every task that generates something**, and a testing task before anything deploys.

**Done when someone could work the list top to bottom without opening the design to find out what comes next** — and when nothing in it is blocked by something further down.
