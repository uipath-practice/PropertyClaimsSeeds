# Build — the case

This is the biggest single piece and the one that fails in the most ways. You already have the design; this is assembly.

Use the **`uipath-maestro-case`** skill and build the case from `sdd.md`, then `uipath-solution` to pack, publish and deploy it. Everything it binds must already exist and be published — that is what your task list ordered.

Check it before you run it:

```bash
python3 3d-case/check_caseplan.py <path-to>/caseplan.json
```

Read that script's comments even if the check passes. Each rule is a shape that packs, deploys and then fails on a live claim, and knowing them changes what you build rather than what you debug.

**Done when a claim with nothing wrong with it goes in and a settled claim comes out, with no human touching it and no task ever raised.** That is the run that proves the whole lifecycle, and the first time you see it you will think nothing happened — the screen you were waiting to answer never appears. Read the record and the timeline instead.

Then prove the four human routes: proceed and refuse at the first gate, approve and deny at the second. Five runs in total.
