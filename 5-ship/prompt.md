# Hand over

Everything runs, `4-verify` proved it and the build is done.

**Pin what runs:** 
- Deployment's version (the package version you last packed and published). Record **the deployment name, package name and version, both folder keys and the case release key** in `PROGRESS.md`. Not the deployment's `Key`. 
- The Coded Action App's deployed version. 
- Last `uip solution upload Build/ClaimCase-<seat> --force`, so Studio Web shows exactly the solution that runs.

**Check what travelled.** 
- The Maestro case and the seven Agents are inside the `.uipx`; 
- The Coded Action App is deployed beside it into the seat folder. 
- Nothing you deployed by hand while building is standing in for a project that is not in the package. 
- A read of the package and the deployments, not a redeploy.

**Bring `sdd.md` to as-built, and mark the work done.** 
- The design outlives the build and everything downstream binds to it, so where the build settled something differently — an SME row closed, a binding renamed, a stage reshaped — the SDD says what was built, with the change recorded in *Design Feedback to PDD* when it touches the process. 
- **Look hardest at what `4-verify` fixed in the case**: a condition that narrows a rule a business user signed is a design change whether or not anyone wrote it down, so it goes in as a Design Feedback row *and* an Action Required row, first to be signed. 
- Add an *As Built* section that states the pins and the known limitations with the change each needs; where it and the design differ, it is right. Every task in `tasks.md` is `[x]` or says why not; `PROGRESS.md` closes with the state of the seat.

**Write the runbook** for a human operating the solution, not the agent that built it: how it is deployed and how it would be promoted, what has to exist first (the six RPA processes, the shared IXP project, the Data Fabric entity, the shared connection), what is known-broken, and what to do when a claim faults. Most of it is already in `PROGRESS.md`; this is a rewrite for a different reader.

**Done when** 
- `sdd.md` describes what runs
- every task is closed
- the runbook exists
- the deployed version is the one you packed
- Studio Web opens the solution that is running.
