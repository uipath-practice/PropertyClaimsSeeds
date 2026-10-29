# Hand over

Everything runs and Verify proved it. Hand the build over so someone else can run it.

Steps:
1. **Pin what runs**: the solution's deployed version, the review app's deployed version, and the names and keys an operator needs, in `PROGRESS.md`. Upload the solution one last time, so Studio Web shows exactly what runs.
2. **Check what travelled**: the case and the seven Agents are inside the solution package, the review app is deployed beside it, and nothing you deployed by hand while building is standing in for something that is not in the package. Read the package and the deployments; don't redeploy.
3. **Bring `sdd.md` up to as-built** with the planner. Where the build settled something differently, the design says what was built, and where that changes the process it is written down for the PDD's owner. Look hardest at what Verify changed in the case: a condition that narrows a rule a business user signed is a design change, and it is the first thing for them to sign. Add an *As built* section with the pins and the known limitations.
4. **Close the work**: every task in `tasks.md` done or saying why not; `PROGRESS.md` ends with the state of the seat.
5. **Write the runbook** for a person operating the solution, not the agent that built it: how it is deployed and would be promoted, what has to exist first, what is known to be broken, and what to do when a claim faults. Open it with the last Verify scorecard.

**Done when:**
- `sdd.md` describes what runs
- every task is closed, except the process app's
- the runbook exists and opens with the last Verify scorecard
- the deployed version is the one you packed
- Studio Web opens the solution that is running.
