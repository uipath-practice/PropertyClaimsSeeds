# Hand over — what bites

| Issue | Fix |
|---|---|
| You cannot read the Coded Action App's deployed version | `uip codedapp` has no `list`, `get` or `status`, and there is no `uip or apps`. `uip maestro case registry search <app>` returns the deployed `SemVersion` and `DeployVersion`; `uip or packages list --search <app>` pins what was *published*. |
| Promotion copies the package and the retrievals resolve to an empty folder | Each provided-automation resource carries this tenant's three bucket keys and the seat folder key as literals (`runtimeDependencies`, `isOverridable: true`); only the per-environment `--config-file` remaps them. Name the three bucket keys in the runbook. Promotion is described, never run: a second deployment is forbidden (`CONFIG.md`, *Deploying*). |
| A check that the source has not changed since the pack keeps failing | `resources refresh` and `solution upload` rewrite `debug_overwrites.json` — leave it out of the comparison. |
| You want to read the deployed case plan back from the package | You cannot. `uip solution pack` re-wraps the case nupkg under another nuspec id (different hash, same content) and ships the compiled BPMN without `caseplan.json`. The plan in git is the only editable copy; say so in the runbook. |
| The runbook's *known-broken* list has nothing about tomorrow | A `PREVIEW` connector's parameter names can move under a deployed case; every claim then faults at its first record write. The runbook names the diagnosis (`uip is resources describe` against the plan's parameter names) and the recovery (`instance migrate` + `instance retry`, `3e-run/cookbook.md`), because the operator who meets it did not build the case. |
