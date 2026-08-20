# Block 5 — getting the case plan built and deployed

The spec is `5-case/spec.md`. This is the platform friction, and there is more of it here than in any other
block. Read the first section before you edit anything: it is the one that costs a day if you meet it cold.

## `caseplan.json` is not what runs — and how to make it run

The file you edit is source. The runtime executes **`caseplan.json.bpmn`**, a compiled artifact sitting beside
it. `solution pack` **copies** that file; it does not build it. So a hand edit to `caseplan.json` can pack,
deploy and run while changing nothing at all, and every symptom points somewhere else.

**`uip maestro case pack` recompiles it, in place, from source:**

```bash
uip maestro case pack <case-project-dir> <throwaway-output-dir>
```

It writes a `.nupkg` you can ignore — the point is the side effect. `caseplan.json.bpmn` beside your source is
rewritten from `caseplan.json`, including the `{"root": ...}` wrapper the runtime requires. Run it after every
edit, before `solution pack`.

**Then prove it, every time:**

```bash
grep -c "<a-token-that-exists-nowhere-else>" caseplan.json.bpmn
```

Pick a string your edit introduces that appears nowhere else — a new task name, a new variable. Zero means the
runtime has not seen your change, whatever the deploy said.

**Do not hand-patch the compiled file.** It is XML with the whole plan embedded as CDATA, and a patched copy
packs cleanly, validates cleanly, deploys cleanly, and then faults at the first element with
`[400013] Case management process metadata missing 'root' property` — because the design-time shape you pasted
in has no `root` wrapper. Delete it and re-pack instead; that is a ten-second fix for a fault that reads like a
platform failure.

If `case pack` refuses with *"JSON is not a valid Case Management JSON of any previous version"*, your plan's
schema version is **newer than the CLI understands** — which happens after a designer round trip, not to a plan
you authored yourself. `uip maestro case debug <project-dir>` recompiles through Studio Web and is the fallback;
it needs a personal robot on your account, and returns `409 ... Cannot find a personal robot configured` if you
have none.

## `uip maestro case validate` may or may not work — check, then pin

It has rejected plans outright with `[version] Invalid input: expected "27.0.0"` while the designer writes
`30.0.0`, and it has also run clean and caught real bugs. **Which you get depends on your CLI version**, and the
CLI moves on its own — it has been observed replacing 1.200.0-preview.117 with 1.199.0-preview.116 mid-session
and calling it an update.

So: try it. If it validates, use it — it catches things the script below cannot, like duplicate task names. If
it refuses on the version, do not downgrade your plan to satisfy it; that is a schema the designer will
overwrite. Either way **log `uip --version`**, because this is the class of result that
is undiagnosable afterwards.

**The gate that always works is the script shipped beside this file:**

```bash
python3 5-case/check_caseplan.py caseplan.json
```

It runs in about a second, needs no tenant, and catches the three classes that fail silently at run time: a
`vars.X` nothing declares, an id pointing at something that no longer exists, and a stage entering on
`exited(...)` from a stage that marks itself complete. Run it after **every** edit, before every pack.

One failure is worth knowing by name: **a stage with no `layout.nodes` entry crashes the Studio Web designer on
load**, with an error naming nothing in your plan (`Cannot read properties of undefined (reading 'x')`). If the
canvas dies after you added a stage, that is why.

## Resolving the processes you bind

Every provided process is found through the registry, and **the registry cache goes stale**:

```bash
uip maestro case registry pull --force
uip maestro case registry search "<process name>" --type process --output json
```

Without the pull you get a partial index — four of six processes, with no indication that two are simply
missing. And **filter the results by folder**: the tenant is shared, other seats have processes with the same
names, and the wrong pick binds cleanly and fails at run time. Check
`Folders[0].FullyQualifiedName == "ClaimCase-<NN>"`.

`uip maestro case tasks describe --type process` does **not** work for classic Orchestrator processes despite
`--help` accepting `process` — it looks in the wrong index and reports no entry found. You do not need it:
`contracts/provided-processes.md` gives every argument and type.

## Build locally; open Studio Web to review

**The build loop needs no designer:**

1. Edit `caseplan.json`.
2. `python3 5-case/check_caseplan.py caseplan.json`
3. `uip maestro case pack <case-project-dir> <throwaway-dir>` — recompiles `caseplan.json.bpmn`.
4. `grep -c` your token in the `.bpmn` to prove the recompile happened.
5. `uip solution pack` / `deploy`.

**Reviewing is a different thing, and worth doing.** A case plan is much easier to read on a canvas than in
JSON, and the designer is where you show someone what you built. But deploying does not put your solution
there — **`uip solution upload <solution-dir>` does**, and it is a deliberate step:

```bash
uip solution upload Build/ClaimCase-<NN>            # first time: imported as new
uip solution upload Build/ClaimCase-<NN> --force    # afterwards: replaces it, wiping its version history
```

Three things to know before you click:

- **Upload before you open, every time.** The sync runs in **one direction only** — opening the project writes
  the tenant's state *down* over your local folder, wholesale, and nothing ever pushes local work up for you.
  Open the designer while local is ahead and local is what you lose.
- **The designer may write a newer schema than the CLI can pack.** If `case pack` starts refusing your plan
  with *"not a valid Case Management JSON of any previous version"* after a visit to the canvas, that is what
  happened, and `uip maestro case debug` becomes your compile step instead.
- **It saves the plan minified onto one line.** Pretty-print after any round trip; formatting is inert.

So the cheap order is: **build and deploy locally, upload once when the block is done, and review there.** If
you want to look mid-build, upload first and expect the local loop to need the fallback afterwards.

## Deploying, and the traps in order

**Uninstall before you pack.** Packing while a deployment is live mints duplicate resources named `..._1` — one
per agent and process the deployment owns — *during* the pack, after any cleanup you ran. Measured both ways: 8
duplicates with the deployment live, zero with it uninstalled, same folder, same files.

The order that works is **uninstall → clean → pack → deploy**.

Cleaning means deleting the numbered files, and the suffix **increments every cycle** (`_1`, then `_2`), so a
`*_1` filter silently stops matching on the second pass:

```bash
find resources -type f -name "*_[0-9].json" -delete
find resources -type f | wc -l          # know your clean baseline and check it
```

**Uninstall refuses while any job is non-final — and it is the *job* that blocks, not the case instance.** An
instance can read `Completed` while its job is still `Running`. Stop the job, and cancel any non-final instance;
a faulted agent leaves a case `Running (With Faults)` forever.

**Raise the list limit or you will not see the blocking job.** `jobs list` returns 50 rows newest-first, and the
parent case job starts *before* every task job it spawns — so its own children push it off the first page. If the
row count equals the limit, the answer is truncated and means nothing.

```bash
uip or jobs list --folder-key <f> --limit 200 --output json \
  | python3 -c "import json,sys,collections; r=json.load(sys.stdin)['Data']; \
                print(len(r), collections.Counter(x['State'] for x in r))"
```

**`Reason: Unauthorized` means "not found".** It appears when a solution pins a package version that is not in the
feed. Nothing is wrong with your permissions and re-authenticating is wasted effort — check the version.

## When a claim does not do what you expected

Two commands answer most of it, and the second settles arguments:

```bash
uip maestro case instance incidents <id> -f <folder>   # the error code and message
uip maestro case instance asset <id> -f <folder>       # the DEPLOYED plan, bindings resolved
```

`asset` returns what is actually running rather than what is in your folder. Most of this block's mysteries are a
difference between those two, so reach for it early.

Reading execution history, expect generated elements you did not author — re-entry counters, variable resets,
parallel gateway markers, per-stage completion trackers. Your own task ids appear verbatim alongside them.

## What a green run does not prove

A case can reach an ending with a stage that never started. Check the stages, not just the outcome: every stage
the claim entered should show complete, and the claim record should carry columns written by each of them. A gap
in the record is a stage that was skipped, and it is invisible anywhere else.

## A task's inputs and outputs are addressed by name, and the names are not yours

Two ways to lose every binding in a plan that packs, deploys, validates and passes
`check_caseplan.py`. Both were measured on 2026-08-20, on the same plan, and each one alone is
enough to stop the case on its first real claim.

### Outputs keep the `out_` prefix

A task output is named for **the argument the automation actually declares**. The extraction
process emits `out_PolicyID`, so the task output is `out_PolicyID` — not `PolicyID`, however much
tidier that looks beside a case variable called `policyId`.

```json
{ "name": "out_PolicyID", "source": "=out_PolicyID", "var": "policyId", "id": "policyId" }
```

`name`/`source` are the automation's side; `var`/`id` are yours. Rename the automation's side and
the output binds to nothing: the variable stays empty, nothing reports it, and the case fails
later at whichever task first reads it — as `170002 ... Value for a required activity argument
'in_PolicyID' was not supplied`, several tasks away from the mistake. Confirm the names rather
than deriving them:

```bash
uip or packages entry-points "<PackageId>:<Version>" --output json    # processes
```

### Connector inputs use `target` + `body`, never `value`

Every other input in a case plan carries its payload in `value`. A connector activity does not:

```json
{ "name": "queryParameters", "type": "json", "target": "queryParameters",
  "body": { "entityScope": "folder", "folderEntityName": "ClaimCase_07" } }
```

Write `value` here and the activity is dispatched with **no query parameters at all**. For a Data
Fabric write that surfaces as the error in the next section, which reads as a missing entity and is
really a missing input.

`check_caseplan.py` catches both classes. `uip maestro case validate` catches neither.

## Writing to a folder-scoped entity: use the V3 activities

Your claim entity lives in your seat folder (`CONFIG.md`), and **the Data Fabric connector's default
activities resolve entity names at tenant level only.** Generate the write tasks the ordinary way and
the case deploys cleanly, then faults on the first row with:

```
[102003] Integration Services bad request — Entity 'ClaimCase_<NN>' not found at tenant level
```

The fix is the V3 form of the same two activities. **Do not hand-author these — generate them**, and
paste the result in:

```bash
uip maestro case spec --type activity --activity-type-id <dfd2bc7a-…> \
  --connection-id <your-connection> --object-name CreateEntityRecord_V3 \
  --input-details '{"queryParameters":{"entityScope":"folder","folderEntityName":"ClaimCase_07",
                    "folderEntityName_folderPath":"ClaimCase-07"},"bodyParameters":{…}}'
```

Ask for the V3 objects by name — the case type cache advertises only V2, and `spec` will build them
anyway. What the generated task carries:

| | create | update |
|---|---|---|
| `objectName` | `CreateEntityRecord_V3` | `UpdateEntityRecord_V3` |
| `method` | `POST` | `PUT` |
| `path` | `/v3/CreateEntityRecord/insert` | `/v3/UpdateEntityRecord/update` |
| `queryParameters` | `entityScope`, `folderEntityName`, `folderEntityName_folderPath` | the same three, plus `recordId` |

Three details that each cost a deploy cycle if missed:

- **The query keys are lower-case** — and `case spec` prints them PascalCased, like everything else
  this CLI displays. `EntityScope` / `FolderEntityName` return `404 Entity ... does not exist`, the
  same error a genuinely missing entity gives. Lower-case them on the way in.
- **There is no `entityName` path parameter.** The entity is identified entirely by the query
  parameters; `pathParameters` stays empty. Confirm it for yourself in one command:

  ```bash
  uip is resources describe uipath-uipath-dataservice CreateEntityRecord_V3 --operation Create
  ```

  Every parameter it lists is `"Type": "query"`. **An earlier version of this cookbook said
  `pathParameters.entityName` was required; it is not, and chasing it cost one build nine deploy
  cycles.** The error that sends you there — `Missing path variables in URL
  .../EntityService/{entityName}/insert` — names Integration Services' *own* downstream URL, and it
  means the entity could not be resolved from the query parameters. Nine times out of ten the query
  parameters never arrived: see `target` + `body` above.
- **The response id is what every later update needs.** Take it from the connector's generic
  `response` output into a case variable, and write that variable to nothing else.

Prove the whole shape without deploying anything:

```bash
uip is resources run create uipath-uipath-dataservice CreateEntityRecord_V3 \
  --connection-id <id> --query "entityScope=folder&folderEntityName=ClaimCase_07&folderEntityName_folderPath=ClaimCase-07" \
  --body '{"claimId":"PROBE-1"}'
```

If that succeeds and the case task does not, the connector and your permissions are both fine and
the difference is in how the task is written — not in the platform. Quote the query string; an
unquoted `&` is a command separator in every shell you might be using.

## Redeploy into the same folder, not a new one

`solution deploy run` refuses a folder that already holds the solution, and the tempting answer — deploy `1.0.2`
into `ClaimCase-02-v102`, `1.0.3` into `-v103` — leaves a folder per attempt, each with fourteen processes, and
by the fifth iteration it is genuinely unclear which one you last ran.

Uninstall, then deploy into the same name:

```bash
uip solution deploy uninstall <solution-name> --output json
uip solution deploy run --package-name <pkg> --package-version <v> \
  --folder-name <same-name-every-time> --parent-folder-path ClaimCase-<NN>
```

`deploy uninstall` takes the deployment **name** as a positional argument and rejects `--deployment-key`, which
is the reverse of most commands here.

## The diagnostics that work, and the ones that do not

When a case run faults, three commands answer and three do not. Reach for the working ones first — the failing
ones return errors about themselves, which is easy to mistake for a broken run.

| Question | Use | Not |
|---|---|---|
| What faulted, and why | `uip maestro case instance incidents <id> --folder-key <k>` | `case job status --detailed` → `unknown_error` |
| Where the case got to | `uip maestro case instance get <id> --folder-key <k>` | `case job traces` → crashes on `null` |
| What is deployed | `uip or processes list --folder-key <k>` | `case process list` → generic error code |

`uip solution deploy list` returns `403` for a participant account in this tenant even when the deploy itself
succeeded. Use `uip or processes list --folder-key <k>` to confirm what landed.

**`uip or jobs start` takes the process GUID**, the `Key` from `processes list` — not the dotted
`ProcessKey` like `ClaimCase-07.Case.ClaimLifecycle`, which fails with `HTTP 400: Undefined process`. Both look
like identifiers and only one is.

`uip or jobs get` and `uip or jobs logs` reject `--folder-key`, though `uip or jobs list` accepts it.
