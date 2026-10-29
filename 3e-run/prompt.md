# Run the case: the clean claim, then the four human routes

The plan is checked but has never run. Deploy it with the **`uipath-solution`** skill and run real claims to find out what it actually does. Several deploy cycles are normal; end each one with a named defect and its fix.

Steps:
1. Deploy, and start one claim on each new version before you start more.
2. Run a claim with nothing wrong with it, and follow it to the end.
3. Aim a claim at each of the four human routes: proceed and refuse at the first gate, approve and deny at the second. The generator takes inputs that plant a problem; a scenario alone does not guarantee a route.
4. Decide the gate tasks from the command line. The review app has no screens yet, so a route that misbehaves now is a case defect.

Guidelines:
- Read the claim record while a gate task is still open, before you complete it. That is what the reviewer will see, and a write that lands only after the gate is hidden once the task is done.
- A broken version costs a whole batch, so prove it on one claim first.

**Done when:**
- a claim with nothing wrong goes in and a settled claim comes out with no human involved and no task ever raised; you checked the claim record and the case timeline
- the four human routes work
- the claim record holds these runs: the next block builds the review screens against them.
