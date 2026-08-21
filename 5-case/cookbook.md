# Block 5 — getting the case plan built and deployed

The spec is `5-case/spec.md`. This is the platform friction, and there is more of it here than in any other
block. Read the first two sections before you edit anything: one is what three builds actually lost time to, the
other is the trap that costs a day if you meet it cold.

## Skills, and the four passes in commands

**Skills.** `uipath-maestro-case`, plus `uipath-solution` to pack and deploy, and `uipath-coded-apps` for the
one small thing in pass 3. **Not `uipath-maestro-bpmn`** — different product; the only thing drawing you there is
that your compiled plan is named `.bpmn`. **Not `uipath-human-in-the-loop`** either — that authors approval nodes
in Flow projects, and your stops are case stages.

**Pass 1 — the journey.** Stages, entry and exit conditions, no tasks.

- Every stage from your design, each with **exactly one way in**.
- Every stage exit names its finishing task or group, and every downstream entry matches how that stage
  leaves — completed against completed, exited against exited. A mismatch is silent at deploy and fatal at run.
- **`edges` stays `[]`** — flow is the conditions, and a stage with no entry condition is unreachable, not
  merely undrawn. **Place every stage in `layout.nodes`** (*Make the canvas readable*, below).
- **No stage that is not in your design**, with one exception `pdd.md` §3 asks for by name.

```bash
uip maestro case validate <caseplan.json> --skeleton --output json     # Valid
```

**Pass 2 — the work and the wiring.**

- Read the deployed automations' exact arguments from the platform, not from memory:
  `uip or packages entry-points "<PackageId>:<Version>"`.
- **A published RPA automation is task type `rpa`**, not `process` (*An Orchestrator automation is `rpa`*, below).
- **One solution, `ClaimCase-<seat>`**, holding the case and all seven agents — a case cannot bind an agent living
  in another solution.
- Parallel work is *grouped*, not sequenced.
- Every stage writes what it produced to the claim record and nothing it did not, through the shared connection,
  using the **V3 activities** a folder-scoped entity needs (*Writing to a folder-scoped entity*, below).

```bash
python3 5-case/check_caseplan.py <caseplan.json>       # 0 problems
uip maestro case validate <caseplan.json> --output json
```

**Pass 3 — the two stops.** Register the stand-in app, then wire a task into each gateway. Both halves are
below: *Registering the stand-in app* and *Wiring an action task*. The app is fifteen minutes and has no design
in it; the wiring is where the traps are.

```bash
python3 5-case/check_caseplan.py <caseplan.json>       # still 0 problems
uip maestro case validate <caseplan.json> --output json
```

**Pass 4 — deploy and run every route.**

```bash
uip maestro case pack <case-project-dir> <throwaway-dir>       # recompiles caseplan.json.bpmn
grep -c "<a-token-your-edit-introduced>" caseplan.json.bpmn    # not 0 — the runtime has your change
```

Then deploy (*Redeploy under the same name*) and run four claims:

| Aim | `in_Scenario` | Should |
|---|---|---|
| the clean one | `auto-settle` | settle with nobody asked |
| stop 1, agree | `eligibility-fail` | carry on into the inspection |
| stop 1, disagree | `eligibility-fail` | end denied |
| stop 2, either way | `review-fail` | end approved, and end denied |

`CONFIG.md` has the shell-quoting trick if you are on Windows. *Answering a stop from the command line*, below,
is how you complete a task with no screen.

A claim sitting in `Running (With Faults)`, or a stage whose tasks are all green while the next stage never
started, is a failure however the status reads.

**Then make it reviewable.** `uip solution upload Build/ClaimCase-<seat>` puts the plan on the Studio Web canvas,
which is far easier to read; deploying alone does not. Read *Build locally; open Studio Web to review* first —
the sync runs one way only.

## Where the time actually goes — read this first

Three builds finished this block. One took **13 solution versions and five authoring bugs**; the other two were
not far off. Every bug had the same shape: **the plan packs, deploys, passes every gate, and then something
binds to nothing.** Not one produced an error naming the thing that was wrong.

So the habit that makes this block cheap is not care while authoring — everyone is careful. It is this:

> **After every run, read the claim record before you read the plan.** An empty column is the shortest path to
> the defect there is. Two of the five bugs below were found that way in a minute each; the two that were not
> cost nine deploy cycles and a wrong conclusion about the platform.

```bash
uip df records query <entity-id> --folder-key <your-seat-folder-key> --output json
```

A stage that went green and left its column empty is a binding that resolved to nothing. A stage missing from
the record altogether never ran, whatever the case's own status says — a case can reach an ending with a stage
that never started, and the record is the only place that shows it.

**Run `check_caseplan.py` after every edit, not before every pack.** It now catches four of the five, in about a
second, without a tenant. The two gates are not substitutes for each other and neither is a substitute for
reading the record:

| | catches |
|---|---|
| `check_caseplan.py` | binding shape, orphan stages, unwritten payloads, exit/entry mismatch |
| `uip maestro case validate` | schema, and `=vars.X` references by their real id |
| the claim record | everything else, which is most of it |

### The five, in the order they were found

1. **A task output that dropped the `out_` prefix** — every binding in the plan resolved to nothing.
2. **Connector inputs written with `value` instead of `target`/`body`** — the activity dispatched with no
   parameters, reported as a missing entity.
3. **A required input bound to an empty-string literal** — dropped from the job entirely, not sent as empty.
4. **`response.X` read from a root-scoped custom output** — silently `undefined`, so every claim looked flagged.
5. **A payload drafted and never written** — the letter reached the claimant's notification and never the record.

The first two are below under *A task's inputs and outputs*; the rest are under *Bindings that resolve to
nothing*.

## Bindings that resolve to nothing, and what each looks like from outside

### An empty string is not an empty value

Binding a required agent input to `""` does not send an empty string — **the runtime drops the key from
`InputArguments` altogether**, and the agent faults at startup on `pydantic: Field required`, naming an input you
did bind. It bites the four analyses downstream of the eligibility gateway, because in pass 1 no human has spoken
yet and `in_EligibilityNotes` has nothing to carry.

Bind a short non-empty literal instead — `"none recorded"` says the true thing and survives the trip. Prove which
keys arrived rather than guessing:

```bash
uip or jobs get <job-key> --output json        # InputArguments as the job actually received them
```

### `response.X` belongs to connector tasks only

A custom output computing a value from an agent's result must read it from the **case variable**, not from
`response`:

```
=js:JSON.parse(vars.decisionJson || '{}').outcome        ✓
=js:JSON.parse(response.DecisionJSON || '{}').outcome     ✗ — undefined on an agent task
```

`response` resolves only inside an `execute-connector-activity`. Elsewhere it is `undefined`, `JSON.parse(...)`
falls back to `{}` via the `||`, and the expression returns a confident wrong answer. One build shipped
`d.outcome !== 'approve'` this way: every claim came out `reviewRequired: true`, including a clean one the agent
had explicitly approved with high confidence. Nothing errored, and the case parked at review exactly as designed.

### A payload with no write task

An agent produced it, the task went green, and no Data Fabric write body mentions it. The claimant's letter went
this way — drafted, used for a notification subject, and never stored, so the record showed a settled claim with
an empty `claimResponseJson`. `check_caseplan.py` warns on every produced payload that reaches no write body;
three of those warnings are expected (raw extraction, prior claims, the poll flag) and a fourth is a bug.

## Registering the stand-in app

Fifteen minutes, no design. What you are producing is a registered app whose **contract** is final and whose page
is blank, because that contract is what the case binds — `contracts/review-task.md` fixes the shape and it is not
yours to change.

```bash
uip codedapp init claim-review-<seat>          # lower case; the tenant is shared
# write action-schema.json to the shape in contracts/review-task.md
npm install && npm run build                   # a page saying "review screen — block 6" is enough
uip codedapp pack dist -n claim-review-<seat> --version 1.0.0
uip codedapp publish -n claim-review-<seat> --version 1.0.0 --type Action
uip codedapp deploy -n claim-review-<seat> --client-id <the-id-in-CONFIG.md> \
  --folder-key <your-seat-folder-key>
```

Four things that each cost somebody an afternoon:

- **`--type Action` on every publish**, first and subsequent. Without it the app registers as a Web app and stops
  binding to Action Center tasks at all.
- **`--folder-key` is your seat folder**, `ClaimCase-<seat>` — never the solution folder your case deploys into.
  Publishing the same app name where two folders could hold it made one seat register **two app identities**: the
  tasks stayed pinned to the first, every later deploy upgraded the second, and nothing said so.
- **Do not create an OAuth client.** One exists and is shared; the id is in `CONFIG.md`, and
  `uip admin external-apps create` will refuse you with `403`, which is the correct answer and not a login
  problem.
- **`action-schema.json` never reaches the package** — pack takes only `dist/`. The platform holds the contract
  from the app's **original registration**, so the schema you register first is the one the case binds. This is
  the whole reason the shape is settled before you start.

**Then tell the solution where the app already is — do not let it make its own.** The app now lives in your seat
folder, but the case binds it and that makes it a solution resource too. Add it as a *remote* resource naming
that folder:

```bash
uip solution resources add --source remote --kind App \
  --name claim-review-<seat> --folder-path ClaimCase-<seat>
```

Skip this and the solution creates a local stub instead, which declares the app in `solution_folder` and pins
whatever version was current when the stub was made. Deploy then installs a *second* copy into the solution
folder while your case binding still says `ClaimCase-<seat>.claim-review-<seat>`, and the run fails with:

```
No app: claim-review-<seat> found in folder: ClaimCase-<seat>
```

which reads as though the app was never deployed. It was — just not where the solution put its copy. **Two seats
hit this on 2026-08-21**, one of them after nine republishes chasing the wrong cause; a third symptom of the same
split is `solution pack` reporting `Unauthorized` when it tries to download a pinned app version that no longer
exists. Whenever you republish the app, re-add the resource rather than editing its package URL by hand.

## Wiring an action task

Two mechanical traps, each of which faulted a live run on a plan that packed and validated cleanly.

**The task's app reference is a binding, not a literal.** `uip maestro case tasks add --type action` writes
`data.name` and `data.folderPath` as plain strings, and that is wrong — like every other non-connector task, an
action task resolves them through `=bindings.<id>` into the plan's root `bindings[]`:

```json
{ "id": "bClmRvName", "resource": "app", "resourceKey": "<folderPath>.<appName>" }
```

Literals pack, validate and deploy, then fault at the first gateway with
`[170015] Internal Server Error: "No app:  found in folder: "` — both values empty, because nothing resolved them.

**A custom output read by the next stage must not sit on the task that closes this one.** Set the decision
variable on the **action task**, not on the write task that also fires the stage's exit: a downstream entry
condition evaluated off `selected-stage-completed` cannot reliably read a value written in the same completion
batch. The symptom is a claim that carries the right decision on its record and routes as though it never
happened.

**Finding the app's id, when the registry will not tell you.** `uip maestro case tasks describe --type action`
wants the *action-app* id, which is not the `systemName` in `.uipath/app.config.json`. `registry pull --force`
reports the node cached and `registry search`/`list` then return nothing for it, at any filter. Read the cache
file directly — `~/.uip/case-resources/action-apps-index.json`, top-level `id`.

**Give the task a title that names the gateway and the seat** — *"Eligibility review for Jane"*. Action Center is
one queue for the whole tenant.

## Answering a stop from the command line

There is no screen yet, so you complete the task yourself:

```bash
uip tasks list --folder-id <folder-id> --output json      # numeric id, not a GUID
uip tasks get <task-id> --output json                     # what the case actually handed it
uip tasks complete <task-id> --type AppTask --folder-id <folder-id> \
  --action "<outcome>" --data '<json>' --output json
```

**`--data` replaces the whole payload.** Send only the outputs and you erase the `inOut` identifiers the platform
would have kept, and the task can never be re-opened — which looks like an app bug in the next block and is not.
Read the task first, merge your outputs into what is there, then complete.

**Assign the task to yourself before completing it.** An unassigned `AppTask` refuses with
`This action is no longer assigned to you`, which reads like a permissions problem and is not — nobody owns it
yet:

```bash
uip tasks users <folder-id> --output json        # who may be assigned
uip tasks assign <task-id> --user <email> --output json
```

**Never put `Action` inside `--data`.** Pass the outcome through `--action` only. Sending both faults the case
at the action task with `170001 Failure mapping the data from the task result`.

### What CLI completion proves, and what it cannot

`tasks get` **PascalCases every key** in the free-form `Data` blob, recursively — `triggerStage` reads back as
`TriggerStage`. That much is only a display artefact. **But a task completed from the command line hands those
PascalCase keys back to the case as well**, so an output mapping sourcing `reviewerNotes` resolves to nothing:
the decision routes correctly because it comes from the *outcome*, while the reviewer's notes arrive `null` and
the next analysis faults on a required input it was promised. Both clean seats hit this independently on
2026-08-21.

So be precise about what this step is for:

| | proven by answering from the CLI |
|---|---|
| all four routes reach the right ending | **yes** — the outcome carries it |
| the identifiers survive a completed task | yes |
| the reviewer's text reaches the record | **no** — block 6 proves that, through the app |

**DocsAI will tell you to make the mapping match the returned field names, and it is right — about the CLI.**
What it cannot know is that the returned casing depends on *who completed the task*, and that the screen arriving
in block 6 returns the other one. Two seats reached that advice independently and one acted on it.

**Do not "fix" this by re-pointing your output mappings at PascalCase.** It makes the CLI run go green and
breaks block 6, where the real app sends the casing your schema actually declares. One seat did exactly that and
carried the fault forward. If a downstream analysis requires a field the CLI cannot populate, make that input
optional for now and note it — the gap closes when the screen exists.

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

**The gate that always works is `check_caseplan.py`, shipped beside this file** — no tenant, about a second,
and every class it catches is one that fails silently at run time. The two gates overlap barely; run both.

## Resolving the processes you bind

Every provided process is found through the registry, and **the registry cache goes stale**:

```bash
uip maestro case registry pull --force
uip maestro case registry search "<process name>" --type process --output json
```

Without the pull you get a partial index — four of six processes, with no indication that two are simply
missing. And **filter the results by folder**: the tenant is shared, other seats have processes with the same
names, and the wrong pick binds cleanly and fails at run time. Check
`Folders[0].FullyQualifiedName == "ClaimCase-<seat>"`.

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
uip solution upload Build/ClaimCase-<seat>            # first time: imported as new
uip solution upload Build/ClaimCase-<seat> --force    # afterwards: replaces it, wiping its version history
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

### `FailedUninstall`, reported as `Validation failed`

That bare phrase is the entire error. It names nothing, it is the single most expensive message in this exercise,
and it almost always means **a job is still running**. Work down this ladder instead of re-reading your plan.

**1. Find the non-final job — and it is the *job* that blocks, not the case instance.** An instance can read
`Completed` while its job is still `Running`, and a faulted agent leaves a case `Running (With Faults)` forever.

**Raise the list limit or you will not see it.** `jobs list` returns 50 rows newest-first, and the parent case
job starts *before* every task job it spawns — so its own children push it off the first page. A row count equal
to the limit is a truncated answer, not an answer.

```bash
uip or jobs list --folder-key <f> --limit 200 --output json \
  | python3 -c "import json,sys,collections; r=json.load(sys.stdin)['Data']; \
                print(len(r), collections.Counter(x['State'] for x in r))"
```

**2. Stop the jobs, then cancel the instances.** A job already `Terminating` cannot be stopped; the one that
clears a stuck case is `uip maestro case instance cancel <id> --folder-key <k>`, which goes `Canceling` →
`Stopped` in seconds.

**3. Retry with a pause.** A second uninstall issued while the first is still settling fails with the *same* bare
message. Wait 15s, then 30s, then 45s before concluding anything.

**4. If it still fails, the deployment record itself is stuck** — it survives even after every job and instance is
final. You cannot inspect it either: `uip solution deploy list` returns `403` for a participant account, so do
not spend time there. Deploy under **`ClaimCase-<seat>-v2`**, write that name in `5-case/notes.md`, and carry on.
This is the one sanctioned departure from the pinned name (`CONFIG.md`, *One deployment, reused*) — it exists so
you are never blocked, and because teardown matches on the `ClaimCase-<seat>` prefix it still finds your work.
**Do not invent any other name**: a deployment nobody can predict is one nobody can clean up.

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
[102003] Integration Services bad request — Entity 'ClaimCase_<seat>' not found at tenant level
```

The fix is the V3 form of the same two activities. **Do not hand-author these — generate them:**

```bash
uip maestro case spec --type activity --activity-type-id <dfd2bc7a-…> \
  --connection-id <your-connection> --object-name CreateEntityRecord_V3 \
  --input-details '{"queryParameters":{"entityScope":"folder","folderEntityName":"ClaimCase_07",
                    "folderEntityName_folderPath":"ClaimCase-07"},"bodyParameters":{…}}'
```

Ask for the V3 objects by name: the type cache advertises only V2 and `spec` builds them anyway. What comes
back:

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

## Redeploy under the same name, every time

`CONFIG.md`, *One deployment, reused*, has the two pinned names and the uninstall-then-deploy pair. Two things
that section cannot tell you until you are here: `deploy uninstall` takes the deployment **name** as a positional
argument and rejects `--deployment-key`, the reverse of most commands in this CLI; and **an uninstalled
deployment never leaves the tenant's Solutions view**, so a name per attempt is permanent, not untidiness you
clear up later.

## Make the canvas readable

A reviewer opening your case in Studio Web should see a process. Two things decide whether they do.

### Do not author edges — they are retired

`schema.edges` stays `[]`, and you never write a `TriggerEdge` or `Edge` object. This is not a rendering
compromise: **stage-to-stage flow is expressed entirely through entry and exit conditions**, and the canvas
derives what it shows from them. `uipath-maestro-case` Rule 20 is correct and current; follow it.

The consequence is worth stating plainly, because it is where the deploy cycles go: **there is no second place
that describes your flow.** A missing edge used to be a cosmetic problem you could see. A missing entry condition
is an unreachable stage that looks identical to a reachable one, and the case simply stops with
*"The case manager returned no actions to execute"*. `check_caseplan.py` fails a stage with no entry condition
for exactly this reason.

### Place the stages yourself

`layout` is canvas state and has no effect on execution, so Rule 18 lets you emit `layout: {}` and leave it to the
frontend. What that produces is a grid in declaration order — endings beside the stage that starts them, waiting
stages inline with the main path, no reading direction. For a plan someone has to *review*, write the map.

**Every node needs an entry or the designer crashes on load** with `Cannot read properties of undefined
(reading 'x')` — an error naming nothing in your plan, so if the canvas dies right after you added a stage, that
is why. `check_caseplan.py` fails an incomplete map for this reason, and accepts an absent one.

The arrangement that reads well, and the one the reference solution uses:

| | x | y |
|---|---|---|
| trigger | 160 | 208 |
| **the main path**, left to right | 320, then **+368** per stage | 224 |
| **a waiting or side stage**, under the stage it hangs off | that stage's x | 768 |
| **terminal stages**, stacked at the right end | last main x **+352** | 224, then **+400** each |

```json
"layout": {
  "nodes": {
    "trigger_1":    { "position": { "x": 160,  "y": 208 }, "style": { "width": 96, "height": 96 } },
    "Stage_Intake": { "position": { "x": 320,  "y": 224 }, "style": { "width": 304 } },
    "Stage_Elig":   { "position": { "x": 688,  "y": 224 }, "style": { "width": 304 } },
    "Stage_Wait":   { "position": { "x": 688,  "y": 768 }, "style": { "width": 304 } },
    "Stage_Apprvd": { "position": { "x": 1776, "y": 224 }, "style": { "width": 304 } },
    "Stage_Denied": { "position": { "x": 1776, "y": 624 }, "style": { "width": 304 } }
  },
  "edges": {}
}
```

Stages are 304 wide; leave the height to the canvas, which measures it from the task count.

## A stage exits on a condition, and a condition nothing can satisfy is a dead case

*"The case manager returned no actions to execute"* means the engine evaluated everything and found nothing
runnable. Every task in the stage can be green when it happens. Three ways to build one, all measured:

- **A stage with no entry condition.** Unreachable, and indistinguishable on the canvas from a reachable one.
- **An exit that names a task which never runs.** An exit rule of the form
  `selected-tasks-completed: [tWrite, tSkip]` gated on `=js:vars.reviewRequired === false` cannot fire if `tSkip`
  is itself conditional on the same flag — the flag being false is now needed *twice*, and the flag being
  anything else blocks the exit permanently. **Gate the exit or gate the task, never both.**
- **An expression against a variable nothing has written.** `undefined === false` is `false`, so a stage whose
  exit tests `=== false` parks forever when the write that should have set the flag silently did not land. When
  a stage will not leave, read the claim record before re-reading the plan: an empty column names the cause.

### An Orchestrator automation is `rpa`, not `process`

The task `type` enum holds both, the skill's own plugin index maps `process` to the process plugin, and nothing
says which one an ordinary published RPA automation is. It is **`rpa`**. Choose `process` — the obvious reading
of the word, since Orchestrator calls the thing a process — and it deploys and runs correctly while every one of
those tasks renders on the canvas with an agentic-process icon. A reviewer then cannot tell the six robot steps
from the seven agents, which is most of what the picture is for.

`process` is for an agentic process. All six provided automations are `rpa`.

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
