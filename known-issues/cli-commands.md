# Commands that fail while the thing they describe is fine

Each of these was met in a real build. In every case the command is wrong, not your solution — and each one
costs a diagnostic detour if you take it at face value.

## `--folder-key` takes a GUID, and a folder *name* fails silently

```bash
uip or processes list --folder-key ClaimCase-01     # looks fine. is not fine.
```

It does not error and does not return zero rows. It returns a **different, paginated, tenant-wide list** —
other seats' processes included — and `HasMore: true`. Every later conclusion drawn from it is wrong, and
nothing anywhere says so.

Pass the GUID. `--folder-path` is the flag that takes a name. Read your folder's key with a JSON reader, never with a filter:

```bash
FK=$(uip or folders list --all --limit 200 --output json \
     | python3 -c "import json,sys; print(next(f['Key'] for f in json.load(sys.stdin)['Data'] \
                                               if f['Name']=='ClaimCase-<seat>'))")
uip or processes list --folder-key "$FK" --output json
```

Three things about that command, each measured: **`--all` is required** or the seat folder is not in the list; **`--output-filter` is refused without an explicit `--limit`** on the 1.201 line (`invalid_argument: … the filter would silently apply to only the first 50 records`) — and when it runs it selects but the envelope stays, so `FK=$(… --output-filter "[0].Key")` captures `{"Result":"Success", … "Data":{"Value":"<the guid>"}}`, not the guid; and **`--name` is a *contains* match**, so `--name ClaimCase-07` returns `ClaimCase-07` *and* `ClaimCase-07-Deploy` in no guaranteed order — exactly the pair you must not confuse (`CONFIG.md`). Match the name exactly, as above. **`--all` belongs to `folders list` alone** — `uip or processes list --all` is rejected; processes paginate with `--folder-key` and `--limit`.

The general form is worth carrying: **any list that comes back bigger than you expected is scoped wrongly**, and
a list that comes back with `HasMore: true` has not answered your question at all.

## `uip maestro case tasks describe --type process` reports no entry found

It accepts `process` and finds nothing. The arguments of a provided automation come from `uip or packages entry-points "<PackageId>:<version>"` (`contracts/provided-processes.md`).

## `uip or packages entry-points` at a wrong version answers `Success` with an empty `Data`

Which reads as *this process declares no arguments* rather than *no such version*. Read the version out of `uip or processes list` first — not all six provided automations are on `1.0.0`. The argument schemas come back as **JSON strings inside the JSON**: parse twice.

## `uip or jobs get` rejects `--folder-key` and double-encodes its outputs

The folder is inferred, so `--folder-key` is an unknown option here. `Data.OutputArguments` is a JSON **string** inside the JSON — parse it a second time before reading `out_*`.

## `uip maestro case spec` PascalCases every key it prints — and drops underscores

Query keys come back `FolderEntityNameFolderPath`; the real parameter is `folderEntityName_folderPath`, lower-case with its underscore, and the underscore cannot be recovered from the print. Take spellings from `uip is resources describe`, never from `spec` (`3d-case/cookbook.md`, *Writing to a folder-scoped entity*). `uip agent debug` does the same to agent outputs: `out_ClaimSummaryJSON` prints as `OutClaimSummaryJSON` — bind the names in `agent.json`.

## `uip solution deploy run --folder-name` always creates a folder, and a wrong `--name` creates a second deployment

`--folder-name` **creates** the folder it names and silently collision-renames when the name is taken — there is no way to deploy into a pre-existing folder by name — except through a matching `--name`: `deploy run` matches an existing deployment **by deployment name** and then acts on it in the folder it already has (pass that folder's current name, collision suffix included), while a name that does not match creates a second deployment in a new folder and reports success twice. One name, forever — `CONFIG.md`, *Deploying*.

## `uip maestro case process run` wants both positionals *and* `--release-key`, the other way round from `--help`

```bash
uip maestro case process run "<dotted PackageId>" <folder-key> --release-key <release GUID> --inputs '{"scenario":"auto-settle","discrepancy":""}'
```

The dotted `PackageId` is the positional; the GUID from `uip or processes list --folder-key <deploy key>` goes in `--release-key`. The GUID alone → *Invalid package key format*; the dotted id alone → *Release key is required. Use 'case process list'* — but **`case processes list` shows only processes that already have instances**, so a never-run case is absent from it. `PackageId:version` and `PackageId@version` → *Invalid process key format*. `--validate` rejects every key shape the run itself accepts. The returned `JobKey` **is** the instance id. Four wrong tries, .

## `uip codedapp deploy` reports a routing-name collision as an app-name collision in the wrong folder

*This app name is already deployed in this folder. Please choose a different name.* — the name is not the problem and the folder in the message is not where the conflict is: the **routing name** is held by another registration of the same app (here, a copy inside a solution package). Find and remove the other registration; do not rename.

## `deploy uninstall` fails with `Validation failed.` and nothing else — a job is not final

`uip solution deploy uninstall <name> --yes` answers `FailedUninstall · Validation failed.` and stops; the Orchestrator Solutions UI shows the same failure **with its cause** — *Jobs are not in final state yet* — which the CLI never prints. The job is in the solution's folder: `uip or jobs list --folder-key <solution folder key> --state Running` (also `Pending`, `Suspended`, `Stopping`), then `uip or jobs stop <job-key> --strategy Kill` (no folder flag), then uninstall again — 24 seconds, `SuccessfulUninstall`, and the name is free. **Do not take the case instances' word for it**: the blocking job belonged to an instance that had read `Completed` for ten hours while its job read `Running` (`lab/findings.md` 186); `instance list` said everything was terminal and it was the jobs that uninstall validates. On the failed record meanwhile, `deploy activate` returns `4007`, `deploy run` on the name `4004 … was not installed successfully` and `deploy upgrade` on the `InstallDeploymentKey` `4005 Another upgrade has already started` — none of them names a job. **The one record the CLI cannot remove** is a `deploy run` that never installed (`Operation: Install / OperationStatus: Failed`, no folder): `uninstall` refuses it and `deploy` has no `delete`; only the Solutions UI deletes it. While a record holds the pinned name, `CONFIG.md`, *Deploying*, says what name to use.

## `uip codedapp deploy` prints an app URL that 404s — the live slug carries `-hitl`

The URL in the deploy output is `https://<org>.uipath.host/<name>`; the app is served at `https://<org>.uipath.host/<name>-hitl`, the routing name it was registered under the first time, kept for the life of the registration however `-n` is spelled afterwards. The plain URL answers *check the app name in the URL*. The true slug is in the served page's `uipath:app-base` meta tag and in the redirect URI deploy appends to the client. .

## `uip codedapp deploy --client-id` answers `400 Failed to update external client redirect URI` — the list is full

The registration holds at most 100 redirect URLs and the message names neither the cap nor the count. `uip admin external-apps get <client-id>` shows the list (`RedirectUri`, comma-separated); a full list is mostly dead entries. The same 400 ends a *solution* deploy whose config carries `externalClientId` (`Apps (FailedInstall): Failed to update external client redirect URI: 400`), and every such deploy that did succeed had appended an anonymous `action-<id>` entry — one per deploy, unattributable afterwards. A standalone app adds one entry named for itself and reuses it. Operator's fix: `infra/provisioning/reset/prune-redirects.sh --dead`; a seat's own entry goes with its reset (`--seat`). `CONFIG.md`, *shared registration*, says why a participant never runs `external-apps update`.

## `uip solution deploy upgrade` reports `UpgradeInitiated` and may never finish

It returns `Result: Success · Status: UpgradeInitiated · FromVersion · ToVersion` in three seconds, and that is all it promises: it records the version change and does not drive the install. twelve upgrades completed on their own; the thirteenth sat at `CurrentPackageVersion <old> · Operation VersionChange · OperationStatus Draft · ActivationStatus Active` for ten minutes — the `Draft` pin a failed first install leaves. It does not poll, has no `--timeout` and takes no `--config-file`. **`deploy list` is the result**: wait for `VersionChange Successful` at the new version. If `Draft` holds, `uip solution deploy run --name <same> --package-version <new> --folder-name "<the folder the deployment already has>"` matches the deployment by name and completes the pending install in place, in 20 seconds. The same `run` on a version no `upgrade` had recorded answered HTTP 400, which is what the skill describes; after the `upgrade` it goes through. Quote the folder name — a collision-renamed folder carries a space.

## `uip maestro case process list` returns a generic error

```
Response returned an error code
```

**Instead:** `uip or processes list --folder-key <key>`, which returns the same processes including the case
itself, with the GUID you need to start it.

## `uip maestro case job status --detailed` and `case job traces` do not report

`job status --detailed` answers `unknown_error`; `job traces` starts streaming and then crashes with
`Cannot read properties of null (reading 'status')`.

**Instead**, and these two answer everything:

```bash
uip maestro case instance get       <instance-id> --folder-key <key>
uip maestro case instance incidents <instance-id> --folder-key <key>
```

## `uip or jobs start` wants the GUID, not the process key

`uip or jobs start ClaimCase-07.Case.ClaimLifecycle` fails with `HTTP 400: Undefined process`. The positional
argument is the `Key` GUID from `uip or processes list` — the dotted string is the `ProcessKey`, a different
field that looks more like an identifier and is not the one.

## `--folder-key` is accepted inconsistently

`uip or jobs list` takes it. `uip or jobs get` and `uip or jobs logs` reject it as an unknown option, and
`jobs logs` without it returns zero rows. `uip or processes delete` rejects it while `processes create` requires it.

There is no rule to learn — check `--help` for the specific verb.

## `uip is connections get` does not exist

Use the `list` form in `known-issues/connections-list.md` and read the entry you want.

## The CLI's self-update reports a failure that does not matter

```
Update completed with failures — Unexpected npm pack output for @uipath/skills
```

It appears mid-command, repeatedly. The command you ran still completes and its result is valid. It is worth
logging once, then ignoring.

## `uip codedapp deploy` refuses every upgrade after the first — `400 invalid app version in request body`

When a second published app model carries the same title (the case's in-solution contract shell and the standalone app both named `claim-review-<seat>`), the CLI resolves the version by *highest wins* — neither model carries `latestInFeed` — and PATCHes the standalone deployment with the shell's deploy version. `--version` cannot find the live version either. The live app keeps working; upgrading needs the right integer in the same PATCH, which no flag supplies. `3f-validation/cookbook.md` has the working order.

## `uip solution deploy list` — `Key` rotates on every version change

`upgrade` takes the current `Key`; `InstallDeploymentKey` stays constant and is refused (`HTTP 400 … not valid`). Re-read `Key` before each upgrade.

## `--output-filter` is JMESPath over `Data`, not over the envelope

`"Data[].{…}"` returns `Result: Success, Data: []` — indistinguishable from an empty tenant. `"[].{…}"` is the form.

## `uip solution publish` rejects the case — `No entry points defined` (error 1205)

`entry-points.json`'s `uniqueId` must equal the compiled BPMN's `uipath:entryPointId` (in `caseplan.json.bpmn`), not an arbitrary string. Re-read it from the BPMN after every `case pack`.

## Data Fabric V3 connector tasks — `entityName` is a path parameter and nothing fills it for you

`case spec --type activity` output groups a write task's inputs into `pathParameters` / `queryParameters` / `body` and leaves `pathParameters` empty; the activity metadata does **not** auto-resolve it. Left empty, every record write fails at runtime — and the full `uip maestro case validate` names it exactly: `Path parameter "entityName" is required … but has no value`. Set it to the entity's name on every Create/Update task.
