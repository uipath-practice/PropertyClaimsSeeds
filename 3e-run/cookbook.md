# Deploying the case and running it — what bites

**The plan passed both gates and neither of them ran anything.** Everything here is a failure that only exists once something executes.

**Compile before you pack.** `uip solution pack` copies `caseplan.json.bpmn`; it never regenerates it — `3d-case/cookbook.md`, *The edit does not take effect*, has the compile command. Check the compiled file is inside the package before you deploy.

## Deploying

| Issue | Fix |
|---|---|
| `deploy run` answers HTTP 400 — a deployment already exists | That is the redeploy path on the 1.201 line: bump the version, `case pack`, `solution pack`, `publish`, then `uip solution deploy upgrade <deployment-key> --version <new>` (the key from `uip solution deploy list`). **`UpgradeInitiated` is not a result** — it records the version change and may not drive the install. Poll `deploy list` until `VersionChange Successful` at the new version; if `Draft` holds after a minute, **`uip solution deploy run --name <same> --package-version <new> --folder-name "<the folder the deployment already has>"` completes it in place** in 20 seconds (`known-issues/cli-commands.md`). `upgrade` takes no `--config-file`, so re-link the shared connection (`deploy config link`) before that `run`. No uninstall — that is recovery, not the loop (`CONFIG.md`, *Deploying*). |
| You are running the deploy loop for the fifth time by hand | Script it — bump → `case pack` → `solution pack` → `publish` → `deploy upgrade` → poll `deploy list` → start a claim → read the record — and make the script **assert the four things that lie**: the compiled `caseplan.json.bpmn` is inside the case nupkg, exactly one deployment carries the pinned name, `deploy list` shows `VersionChange Successful` at the new version (`UpgradeInitiated` alone is not that), and the Data Fabric record (not the job status) shows the write. `set -e`; a script that swallows an exit code is worse than typing. Time each step and write the numbers into `PROGRESS.md`. Measured 2026-08-27: a cycle is **5–8 minutes** end to end, of which the deploy itself is 60–90 seconds and a claim run is 8–14 minutes; twelve cycles in two hours. |
| A redeploy creates a second deployment | Same name, every time — `CONFIG.md`, *Deploying*; `deploy run --folder-name` and a non-matching `--name` are in `known-issues/cli-commands.md`. |
| Publishing rejects the package | The feed refuses a duplicate name and version. Bump the version — never rename the solution. |
| `deploy uninstall` answers `Validation failed.` and nothing more | A job in the solution folder is not final — here a case job still `Running` under an instance that read `Completed`. `uip or jobs list --folder-key <solution folder> --state Running`, `uip or jobs stop <key> --strategy Kill`, uninstall again; 24 seconds. The Orchestrator Solutions UI shows the reason the CLI drops (`known-issues/cli-commands.md`). |
| A bound automation is not found, five seconds in, having executed nothing | The folder. `contracts/provided-processes.md`, last section. |

## When a claim does not do what you expected

Read the instance, not the job list. Four commands answer almost everything, all with `--folder-key <the deploy folder>`: `uip maestro case instance get`, `instance variables`, `instance incidents`, `incident get`. **`instance variables` is the only useful view and it is awkward** — case globals are spread across every `adhocCaseEventSubProcess` / `tasksEventSubProcess` snapshot (merge them latest-non-null-wins); `CaseState.StagesEntered / StagesExited / StagesCompleted / TasksCompleted` is the timeline; task outputs are in `tasksEventSubProcess[].TaskCompletedOutputsVariable`, keyed by PascalCased task display name. The incident detail is long and **the cause is at the end**, not the start.

**There is no log and no trace for a case job** — `uip or jobs logs` returns zero rows, `uip traces spans get --job-key` zero spans. For an Agent or RPA fault the detail is in the **child job**: `uip or jobs list --folder-key <folder>`, then `uip or jobs get <key>` — `Info` carries the message; `InputArguments` / `OutputArguments` are JSON strings inside the JSON, so parse twice. `instance list --folder-key` does **not** filter: other seats' instances come back too.

| Issue | Fix |
|---|---|
| `uip tasks list` on the deploy folder returns 0 and there is no incident, so the gate looks silently broken | **The task appears in the folder that holds the app**, not the folder that holds the case — list the seat folder. Measured 2026-08-27; it cost four deploy cycles chasing a gate that worked. |
| `uip tasks complete` says *This action is no longer assigned to you* on a task nobody has touched | A case-raised task is `Unassigned` and cannot be completed until it is claimed: `uip tasks assign <id> --user <email>` first, then complete. |
| Route runs are eating the afternoon | Run the four human routes **concurrently** — each mints its own claim id and nothing interferes. Five claims in parallel finished in 15 minutes; sequentially they take an hour. |
| An `auto-settle` claim escalates and you reach for the Agent's prompt | An `auto-settle` claim is not guaranteed to clear every check — the assessor reports carry per-incident-type boilerplate that can genuinely contradict the scope. Check a second claim before touching a prompt; one escalating report is not evidence an Agent is broken. |
| A `Draft` deployment pinned to an old version refuses every newer one | *cannot deploy 1.0.2 until you complete the deployment of 1.0.0* — a failed first install leaves a Draft. `deploy uninstall --yes` clears it. |
| `deploy config get` says *File not found* straight after `publish` | The package needs a few seconds to index. Retry. |

## Bindings that survive both gates and still misbehave at run time

| Issue | Fix |
|---|---|
| The very first record write faults with `Value uniqueness violation … Error Number: 2627` and names nothing you recognise | `claimId` is unique on the entity (`contracts/claim-entity.md`) and you re-ran a claim that already has a row. Every run is a new claim id; to repeat one, delete its row first — `uip df records query … --folder-key`, then `records delete`. |
| A component receives the literal name of an output instead of its value | A bare output name is a **string**, not a reference. Every task goes green and every field downstream is blank. |
| A polling loop overwrites a good result with a later empty one | A stage that re-enters re-runs its calls. **Guard the write**, or a ready result is replaced by the next not-ready one. |
| A routing guard sends a claim down the wrong lane | The value it tests may not be written yet at the moment the gate evaluates. `'' !== 'Deny'` is true, and a denied claim goes down the approved path with a letter that says otherwise. **Test for the outcome you want, not against the one you don't.** |
| A resources refresh reports `Created 0, Imported 0, Skipped 0` | The counter is unreliable in both directions. **The resources tree on disk is the truth** — check it wrote files rather than believing the number. |

## Measured on the Opus03 run, 2026-08-28

| Issue | Fix |
|---|---|
| `deploy upgrade <key>` answers `HTTP 400 … not valid` | `deploy list`'s `Key` **rotates on every version change**; `InstallDeploymentKey` does not, and `upgrade` wants the *current* `Key`. Re-read it from `deploy list` before every upgrade; `ProcessVersion` on that row is how you confirm what is installed. |
| `deploy config link` accepts the Action App and the deploy then fails | Linking is accepted locally (`Result: Success`) and rejected by the server — **only the connection is linkable**; the app is provisioned by the deploy from `solution_folder`. `deploy config unlink … <app>` clears it. |
| `scenario: eligibility-fail` did not open H1; `review-fail` settled itself | **A scenario does not guarantee a route** — of two `eligibility-fail` claims started together one failed screening and one did not. Pin the route with `in_Discrepancy`: pass an invalid id and the generator's fault lists the valid ones (`REVIEW_AMOUNT_INFLATION`, `REVIEW_CAUSE_MISMATCH`, …) — no answer key needed. |
| Two claims faulted in the same two seconds, `170002 / HTTP Request Failed` | The LLM provider, not the build — the real cause is in the child job (`uip or jobs get <key>`, `Info`). `uip maestro case instance retry` recovered both in place. |
| The app cannot parse `failedChecks` | It is an array of bare rule-id strings on some claims and of objects (`{ruleId, name}`) on others, from the same agent. Handle both. |
