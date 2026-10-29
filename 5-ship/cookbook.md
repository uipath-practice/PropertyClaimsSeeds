# Hand over

## How it is built here

- **Pins in `PROGRESS.md`**: the deployment name, the package name and version, both folder keys (seat and `-Deploy`) and the case release key; never the deployment's `Key`, which rotates. The Coded Action App's deployed version. Then `uip solution upload Build/ClaimCase-<seat>`.
- **As built**: the planner owns the edit. A condition Verify narrowed goes in as a *Design Feedback to PDD* row **and** an *Action Required* row. The *As Built* section states the pins and each known limitation with the change it needs; where it and the design differ, it is right. Every task in `tasks.md` is `[x]` or says why not.
- **The runbook** names what has to exist first: the six RPA processes, the shared IXP project, the Data Fabric entity, the shared connection. Its scorecard: each planted problem caught or missed, the clean-claim referral rate against SC5, the next fix for every open failure. Most of it is already in `PROGRESS.md`; rewrite it for an operator.

## What bites

| Issue | Fix |
|---|---|
| You cannot read the Coded Action App's deployed version | `uip codedapp validate --path-name <app>` reads the live deployment; `uip or packages list --search <app>` pins what was *published*. `uip maestro case registry search <app>` answers from a local cache that stays on the old version until `registry pull -f`. |
| Promotion copies the package and the retrievals resolve to an empty folder | Each provided-automation resource carries this tenant's three bucket keys and the seat folder key as literals (`runtimeDependencies`, `isOverridable: true`); only the per-environment `--config-file` remaps them. Name the three bucket keys in the runbook. Promotion is described, never run: a second deployment is forbidden (`CONFIG.md`, *Deploying*). |
| You want to read what was published | `uip solution packages download <name> <version>`: the case nupkg inside carries `content/caseplan.case`, and comparing it with `Build/` shows what travelled. What you cannot read back is the plan as deployed in Orchestrator. |
| `deploy list --folder-key <deploy folder>` returns `[]` | It filters on the parent folder: pass the seat folder key. |
| The runbook's *known-broken* list has nothing about tomorrow | A `PREVIEW` connector's parameter names can move under a deployed case; every claim then faults at its first record write. The runbook names the diagnosis (`uip is resources describe` against the plan's parameter names) and the recovery (`instance migrate` + `instance retry`, `3e-run/cookbook.md`), because the operator who meets it did not build the case. |
