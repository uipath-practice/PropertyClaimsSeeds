# Run Maestro Case and test it: the clean claim, then the four possible routes involving human review

Case Plan is checked, but not tested yet on real claims. Compile, Pack, Publish and Deploy with the **`uipath-solution`** skill. Run it to find out what the plan actually does. It is normal for it to take several deploy cycles, each one should end with a named defect and fix.

Aim each run with the case's own `scenario` / `discrepancy` inputs (and `profileId` to repeat a claimant) — they flow to the generator (`contracts/provided-processes.md`, *Retrieve Property Claim*); a scenario alone does not guarantee a route, a pinned `discrepancy` does (`cookbook.md`).

Complete the Action Center tasks from the command line (`uip tasks complete`) — the Coded Action App has no screens yet, only the empty-page registration the case binds. A route that misbehaves now is a case defect; the point is to find case-plan issues before the app is live.


**Done when:**
- a claim with nothing wrong with it goes in and a settled claim comes out, with no human touching it and no task ever raised. That is the run that proves the whole case (happy path), the Action Center task never appears. Read the Data Fabric record and the case instance's timeline instead.
- four human routes proven: proceed and refuse at the first gate, approve and deny at the second. 

Five runs in total. The Data Fabric record populated by the end of this block: the next block builds the Action App's screens against these payloads.

