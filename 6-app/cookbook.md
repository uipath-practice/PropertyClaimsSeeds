# Building the reviewer's screen — how to get it done here

The platform mechanics, the order that works, and what has cost other people time. It assumes you can read the
SDK's own docs and is about the parts they do not mention.

**Skills.** `uipath-coded-apps` for the app itself; `uipath-tasks` when you need to inspect or drive an Action
Center task from the command line. Not `uipath-human-in-the-loop` — that authors approval nodes in Flow
projects, and your gateways already exist in the case plan.

## Where the time goes, and the order that avoids it

Build it in this order. Each step is provable on its own, and the ones that go wrong go wrong for reasons the
next step would hide.

1. **Get a real task payload in front of you before writing any UI.** Send a claim in, let it stop, and read what
   actually arrives. Everything downstream is shaped by it, and guessing costs a rebuild.
2. **Get the claim out of Data Fabric**, from a plain script, with the app's own credentials. This is where the
   scope problem below bites, and it bites the same whether you meet it now or after building three screens.
3. **Render read-only**, both gateways, no controls. Now the "explicitly unavailable" sections are visible and
   cheap to fix.
4. **Add the decision and complete a task.** Approve on one claim, reject on another.
5. **Check the claim record**, not the screen. This is the step people skip.

The two that reliably cost an afternoon are 2 and 5, and both are invisible from the front end.

## Naming and where things go

| | |
|---|---|
| App name | `claim-review-<NN>` — the tenant is shared and app names collide |
| Source | `Build/ClaimCase-<NN>/claim-review/` |
| Deployment | its own; a coded app is **not** part of the `.uipx` solution and deploys separately |

The app is registered against the case's two gateway tasks, so the case plan gains a task at each gateway that
binds to it. That is a case-plan edit — expect to go back to block 5's edit loop once, and read
`5-case/cookbook.md`'s recompile step before you do, because the compiled plan is what runs.

## An app that reads a new service needs its scope, and the error names neither

Adding one SDK service to a working app can break the whole app, because each service needs its own OAuth scope
and the refusal names neither the service nor the scope:

```
You are not authorized!
```

That is the entire message, and it kills **every** service, not only the new one — asking for a scope the app
does not hold fails the token fetch outright. So an app that worked, plus one Data Fabric call, equals an app
that shows nothing at all.

**Two separate things have to agree**, and this is where the afternoon goes:

| | Where it lives | What it means |
|---|---|---|
| The **grant** | the External Application registration in Automation Cloud | what the app is *allowed* to ask for |
| The **request** | `uipath.json`, which ships **inside** the app package | what it *does* ask for |

Editing the registration alone changes nothing, because the deployed app still requests the old list — the config
travels in the package, so the scopes are frozen at the version being served. Symptom: you fix the registration,
reload, and get the identical error, repeatedly.

The fix is both halves: grant it on the registration, **and** publish a new app version carrying the updated
`uipath.json`.

```bash
uip admin external-apps get <client-id> --output json    # what is actually granted
```

The two drift quietly — one build had a scope granted that `uipath.json` did not list, so neither file was
evidence for the other. Check both.

## Reading the task, and the session you are already in

- **Never call `sdk.initialize()`.** Inside Action Center the host injects a session; construct the client and
  use it. Initialising your own is how an app works in a browser tab and fails in the place it is meant to run.
- **Await the task fetch.** No timeout race, no fallback. One prototype raced a 2-second timer against the fetch
  and could show sample data *inside Action Center* — which is the failure the no-mock rule in `spec.md` exists
  to prevent, arriving by a side door.
- **Every list call returns one page.** Loop the cursor to completion; a single call is never "all rows".
- **A completed task is a distinct state and the platform tells you which.** Read `task.isReadOnly` and render a
  read-only summary. Branching on a platform-supplied mode is not defensive parsing.

## Getting a document onto the screen

Three PDFs, two ways to reach them, and they fail differently — choose deliberately rather than by whichever the
SDK docs open on.

**As a job attachment.** A process that outputs a file leaves it in Orchestrator addressed by a GUID. Resolve it
with `attachments.getById(id)` for a `blobFileAccess` descriptor — `{ uri, httpMethod, requiresAuth, headers }` —
fetch, make a blob URL, render. Needs `OR.Folders`. Not folder-scoped: a GUID is addressable on its own.

**As a bucket file.** The same PDF sits in a bucket under a filename. `buckets.getByName(name, { folderPath })`
for the numeric id, then `buckets.getReadUri(bucketId, path, { folderPath })` — **the same descriptor shape**, so
the fetch-and-render half of your code is identical. Needs `OR.Buckets.Read`, and the folder is not optional.

**Prefer the id, fall back to the derived path.** An attachment id is a reference that has to survive every hop
from producer to consumer — process output, case variable, entity column, task, app — and it can arrive empty at
any of them, always with the same symptom: your app says the document is not there, which reads like an app bug
and is not. A bucket path is derived where it is used, from identifiers the record already holds, so nothing has
to carry it and nothing can drop it. Written both ways, the app also repairs itself if ids start arriving again.

Two things the fallback has to get right:

- **Derive a path only for a document that should exist.** A filename is predictable long before the file is: the
  surveyor's report has a computable name from the moment a claim has a number, and no file until an inspection
  has happened. Gate it on something that proves the document exists — the report's own extracted payload, say —
  or a reviewer gets a button that 404s where they should have read "no report filed yet".
- **Say what you looked for when it fails.** `Claims/CLM-…-claim.pdf did not resolve: <reason>` is actionable.

### Where the files are, and why the folder matters

Buckets are **linked into** a solution folder from the folder that owns them, not provisioned inside it — a
solution subfolder does not inherit its parent's buckets. So every bucket call names the folder holding the
bucket, which is *not* the folder your app runs in. That path is the one environment-specific value the app
carries: name it once, in one place.

The numeric bucket id is tenant-local and changes if a bucket is recreated. Look it up by name, cache for the
session, never write it into source.

```bash
uip or buckets list --folder-key <folder> --output json          # names, keys, numeric ids
uip or bucket-files list <bucket-key> --folder-key <folder>      # the paths actually present
```

The second answers "is the app wrong, or is the file simply not there" — worth settling before reading any app
code. Paths resolve with or without a leading slash.

## How to test it

### Make a claim stop at the eligibility gateway

Aim the run. `Retrieve Property Claim` takes `in_Scenario`, and `eligibility-fail` produces a claim the screening
analysis will flag:

```bash
uip or jobs start <process-key> --folder-key <your-seat-folder-key> \
  --input-arguments '{"in_ClaimID":"<claim-id>","in_Scenario":"eligibility-fail"}' --output json
```

For the second gateway use `review-fail`, which passes screening and is flagged by the analysis instead. The full
matrix is block 7's; two aimed runs are all this block needs.

### Find the waiting task

```bash
uip tasks list --folder-id <folder-id> --output json      # numeric id, not a GUID
uip tasks get <task-id> --output json                     # the payload your app receives
```

`tasks get` is also how you inspect what actually arrived without instrumenting the app. One caveat worth
knowing: it **PascalCases every key** in the free-form `Data` blob, recursively — `triggerStage` reads back as
`TriggerStage`, `claim_id` as `ClaimId`. The values and their types are honest; only the key casing is not. Do not
reshape your app to match what this command prints.

### Then check the claim record, not the screen

```bash
uip df records query <entity-id> --folder-key <your-seat-folder-key> --output json
```

The decision, the reviewer's words and the time all belong on the row. **A screen that submits successfully and
stores nothing looks identical from the front** — this query is the only thing that tells them apart, and it is
the check builds skip.

### Two runs, not one

Approve one claim and reject another. A screen wired only for the happy answer looks finished and fails the first
time a reviewer disagrees — and the denied path is a different ending in the case plan, so it exercises wiring the
approval never touches.
