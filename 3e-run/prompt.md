# Build — deploy the case and prove the lifecycle

The plan is authored and both gates passed. Neither of them ran anything. This block is where you find out what the plan actually does, and it is normal for it to take several deploy cycles — each one should end with a named defect, not a guess.

Pack, publish and deploy with the **`uipath-solution`** skill. **Compile the case plan first** — `3d-case/cookbook.md`, *The edit does not take effect*, has the command and the reason.

**Done when a claim with nothing wrong with it goes in and a settled claim comes out, with no human touching it and no task ever raised.** That is the run that proves the whole lifecycle, and the first time you see it you will think nothing happened — the screen you were waiting to answer never appears. Read the record and the timeline instead.

Then prove the four human routes: proceed and refuse at the first gate, approve and deny at the second. **Complete those tasks from the command line** — the validation app does not exist yet, and that is deliberate: a route that misbehaves now is a case defect, and finding it here means you are never debugging the plan and the screen at the same time.

Five runs in total. **The record has to be populated by the end of this block** — the next block builds a screen that reads it, and a screen with nothing to render cannot be judged.
