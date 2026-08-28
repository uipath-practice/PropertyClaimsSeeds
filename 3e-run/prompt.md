# Build — deploy the Maestro case and prove it: the clean claim, then the four human routes

Case Plan is checked, but not ran yet. Run it to find out what the plan actually does. It is normal for it to take several deploy cycles, each one should end with a named defect and fix.

Pack, publish and deploy with the **`uipath-solution`** skill. **Compile the case plan first** — `3d-case/cookbook.md`, *The edit does not take effect*.

**Done when a claim with nothing wrong with it goes in and a settled claim comes out, with no human touching it and no task ever raised.** That is the run that proves the whole case (happy path), the Action Center task never appears. Read the Data Fabric record and the case instance's timeline instead.

Then prove the four human routes: proceed and refuse at the first gate, approve and deny at the second. **Complete those Action Center tasks from the command line** (`uip tasks complete`) — the Coded Action App has no screens yet, only the empty-page registration the case binds. Route that misbehaves now is a case defect, objective is to detect case plan issues before app is live.

Five runs in total. **The Data Fabric record has to be populated by the end of this block** — the next block builds the Action App's screens against these payloads, and a screen with nothing to render cannot be judged.
