# Hand over — what bites

| Issue | Fix |
|---|---|
| You want to prove the package runs somewhere it has never run | Not in this workshop — a second deployment into another folder is forbidden (`CONFIG.md`, *Deploying*) and an uninstall-and-redeploy loses every running instance for a proof `4-verify` already gave. Promotion is the same package in another **tenant** with its `--config-file` (*Promotion*, below); describe it in the runbook. |
| The deployment key you recorded is gone | `Key` tracks the latest operation record and rotates; `InstallDeploymentKey` is the one `deploy upgrade` takes. Pin the name, the package name and version, the folder key and the case release key — none of them move. |
| `uip solution deploy status <any id from deploy list>` → `404 PipelineDeploymentNotFound` | It wants the transient pipeline id from the `deploy run` output. After the fact, `deploy list` is the status and `uip or processes list --folder-key <deploy folder>` is the per-component confirmation. |
| You cannot read the Coded Action App's deployed version | `uip codedapp` has no `list`/`get`/`status`, and there is no `uip or apps`. `uip or packages list --search <app>` pins what was *published*; the deployed version is taken on the deploy's own output. |
| Promotion copies the package and the retrievals resolve to an empty folder | Each provided-automation resource carries this tenant's bucket keys and seat folder key as literals (`runtimeDependencies`, `isOverridable: true`). The per-environment `--config-file` is the remap; without it nothing is remapped. Name the three bucket keys in the runbook. |
| An `AppV2` package version for the app sits in the tenant feed | The in-solution registration from before the app moved beside the solution. Nothing references it; deleting a published version is a tenant action for no gain — record it and leave it. |
| You want to read the deployed case plan back from the package | You cannot. `uip solution pack` re-wraps the case nupkg under another nuspec id (different hash, same content) and **drops `caseplan.json`** — the package carries the compiled BPMN only. The plan in git is the only editable copy; say so in the runbook. |
| `uip or releases list` on the deploy folder returns nothing | A solution-deployed case has no release row there. The case release key is the `Key` on `uip or processes list --folder-key <deploy folder>` for the case process. |
| The runbook's *known-broken* list has nothing about tomorrow | A `PREVIEW` connector's parameter names can move under a deployed case with nothing redeployed; the first symptom is every claim faulting at its first record write. Name the diagnosis (`uip is resources describe` against the plan's parameter names) and the recovery (`instance migrate` + `instance retry`) in the runbook, because the operator who meets it will not have built the case. |
| The final `uip solution upload --force` is refused as a deploy | It publishes nothing and cannot be deployed from; the refusal is the harness classifier, not the platform, and the same command ran in every earlier block. Re-run it, or have your operator run it, and pin Studio Web's state from the upload's `Action` line. |

## Promotion is pack once, deploy many

One package, then per environment set the tenant, publish, and deploy with that environment's configuration. **Repacking per environment is how two environments end up running different code with the same version number.**
