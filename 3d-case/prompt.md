# Build — the case

This is the biggest single piece and the one that fails in the most ways. You already have the design; this is assembly. **You are authoring here, not running** — deploying and proving the lifecycle is the next block, and keeping them apart is what stops a bad plan being debugged through five deploy cycles.

Use the **`uipath-maestro-case`** skill and build the case from `sdd.md`. **The two human gateways bind `contracts/review-task.md`** — an app registered with that shape and an empty page is enough to wire and prove them, and changing the shape later clears both bindings. Everything it binds must already exist and be published — that is what your task list ordered.

Check it before you go any further:

```bash
python3 3d-case/check_caseplan.py <path-to>/caseplan.json
```

Read that script's comments even if the check passes. Each rule is a shape that packs, deploys and **then** fails on a live claim, and knowing them changes what you build rather than what you debug.

**Done when both gates are green and the plan opens in the designer** — `uip maestro case validate` reports `Valid`, `check_caseplan.py` reports no referential problems, and the diagram reads as the process: the lifecycle left to right, endings on the right, each secondary lane under the stage it branches from (`cookbook.md`, *Canvas*). Two different questions: one asks whether the platform accepts it, the other whether it can do anything.
