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
| App name | `claim-review-<seat>`, **lower case** — the tenant is shared and app names collide |
| Source | `Build/ClaimCase-<seat>/claim-review/` |
| Deploy into | **`ClaimCase-<seat>`, your seat folder** — never `ClaimCase-<seat>-Deploy` |
| Deployment | its own; a coded app is **not** part of the `.uipx` solution and deploys separately |

**You registered this app in block 5** as an empty page with its final contract, and you are replacing the page,
not the app. Same name, same `action-schema.json`, new version. Do not register a second one, and do not change
the schema — the case is bound to it, and re-registering clears the task's bindings at both gateways
(`contracts/review-task.md`).

**The folder is the one that bites.** Publishing the same app name while two folders could plausibly hold it —
your seat folder and the solution folder your case deployed into — got one seat **two app identities under one
name**. Tasks already raised stayed pinned to the first; every later deploy upgraded the second; the app being
fixed and the app being opened were different apps, and nothing said so. The tell is
`.uipath/app.config.json`'s `systemName` no longer matching the `AppId` on an existing task:

```bash
uip tasks get <task-id> --output json     # AppTasksMetadata.AppId
cat .uipath/app.config.json               # systemName — these two must agree
```

If they have diverged, deploying again will not converge them. Stop and check before you publish a second time.

**And if you already have two, there is a way out.** `uip codedapp publish` resolves the app **by name alone** —
it does not read `app.config.json`'s `systemName`, and restoring that file by hand does not help. With two
records sharing a name, five consecutive publishes alternated between them **deterministically**: 1.1.0 → A,
1.1.1 → B, 1.1.2 → A, 1.1.3 → B, 1.1.4 → A. So: after every publish read the **System Name** the command prints
back, compare it to the `AppId` on an existing task, and if it is the wrong one **bump the version and publish
again** until it is the right one. Deploy the version that landed on the bound identity. It costs a version
number per attempt and nothing else.

**If your gateways are not already wired** — a case plan built before this block existed in its current
shape — do that first: `5-case/cookbook.md`, *Registering the stand-in app* and *Wiring an action task*. Then come
back. Everything below assumes a claim can already reach a task and be answered.

## The OAuth client already exists — do not create one, and do not edit it

The client id and the scopes are in `CONFIG.md`. Copy them into `uipath.json`, pass the id to `deploy`, and move
on. Three separate builds each lost most of an hour here and none of it was necessary.

```bash
uip codedapp deploy -n claim-review-<seat> --client-id <the-id-from-CONFIG> --folder-key <seat-folder-key>
```

What you will otherwise walk into:

- **`uip admin external-apps create` returns `403`.** Managing OAuth clients is a tenant-wide right this exercise
  does not grant. This is the expected answer, not a login problem — and the skill's own troubleshooting will
  encourage you to fix the registration yourself, which you cannot and must not.
- **`uip admin external-apps list` may also `403`.** So you cannot confirm the grant by reading it. `CONFIG.md`
  is the source of truth; treat it as read.
- **Two Data Fabric resources exist and picking the wrong one costs you a day.** `uip admin scopes list` shows
  both: `DataFabricOpenApi` with `DataFabric.*`, and the older `DataServiceOpenApi` with `DataService.*`. The
  TypeScript SDK calls `/datafabric_/` exclusively, so **`DataFabric.*` is the pair you need** — `CONFIG.md` has
  the exact string. Get it wrong and the token authenticates cleanly and reads nothing, reporting
  `Missing permissions: EntityRecords.View` in your seat folder. That is a *folder permission* message for a
  *scope* fault, so it sends you to check folder roles, effective permissions and the entity's folder, all of
  which will look correct. Grep the SDK if you are ever unsure which API a call lands on:
  `grep -roh "datafabric_\|dataservice_" node_modules/@uipath/uipath-typescript/dist/`.
- **`deploy` registers your redirect URL on the shared client for you.** Never run
  `uip admin external-apps update` — it **replaces** the redirect list rather than appending, so on a shared
  client it breaks everybody else's app in one command.

**If a call still fails on authorisation, the fault is in `uipath.json`, not in the registration.** The scope
list travels *inside the app package*, so it is frozen at the version being served — a config you fixed locally
and did not republish is not the config running. The message gives you nothing to go on:

```
You are not authorized!
```

That is the whole error, and it kills **every** service rather than the one that is short a scope, so an app that
worked plus one new Data Fabric call is an app that shows nothing at all. Republish; do not go looking at the
registration.

## Reading the task, and the session you are already in

- **Never call `sdk.initialize()`.** Inside Action Center the host injects a session; construct the client and
  use it. Initialising your own is how an app works in a browser tab and fails in the place it is meant to run.
- **Await the task fetch.** No timeout race, no fallback. One prototype raced a 2-second timer against the fetch
  and could show sample data *inside Action Center* — which is the failure the no-mock rule in `spec.md` exists
  to prevent, arriving by a side door. The rule is that nothing which fails, times out or arrives malformed may
  fall through to invented data; a dev-only branch taken *before* the fetch is not that, and
  *Running it locally* below depends on it.
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

**The CLI takes the `Key`; the SDK takes the numeric `Id`.** Both come back from `buckets list`, and passing the
number to the CLI fails with `Invalid bucket key: '24070'. Expected a UUID` — which reads like a broken value
rather than the wrong one of two.

The second answers "is the app wrong, or is the file simply not there" — worth settling before reading any app
code. Paths resolve with or without a leading slash.

## How to test it

### Park your tasks — this is the difference between an afternoon and a morning

A full case run costs two to three minutes before your screen appears, and the instinct is to run one per change.
Do not. **A waiting task stays waiting until you complete it, and you can reload the app against it as many times
as you like.**

So before you write any UI, send in **three claims to each gateway** and leave them parked. Now every iteration
is a browser reload. Spend a task only when you are deliberately testing the decision itself, and you still have
two left at that gateway.

**Working on the record read?** Query the entity from a script. The screen is not involved and neither is the
case.

### Match the loop to what you actually changed

A full run is the only one of these that re-proves the journey, and it is the only one that costs minutes. Most
of block 6 does not touch the journey, so most of block 6 should not be paying for one.

| What you changed | Cheapest thing that shows it | Cost |
|---|---|---|
| Layout, wording, an empty state | `npm run dev` against a captured payload | a reload |
| How the app reads one value | edit the row, reopen the parked task | seconds |
| App code, running where it really runs | redeploy, reopen the parked task | about a minute |
| The task payload, a gateway, the routing | an aimed run | 2–3 minutes |

**The two middle rows are the ones builds skip**, and between them they cover most of the work.

**Change what the claim says instead of waiting for a claim that says it.** A parked task points at a row; edit
the row and reload the task. `update` is a partial write — name the `Id`, then only the columns you want moved:

```bash
uip df records update <entity-id> --folder-key <seat-folder-key> \
  --body '{"Id":"<record-id>","<column>":"","<another>":0}'
```

That is how you see a missing surveyor report, a zero settlement, or a reviewer's reason long enough to break
the layout — in seconds, instead of running claims until one turns up. `insert` builds a whole row from nothing
the same way, when you want a claim no run has produced.

### Running it locally, and the three seconds that look like a hang

`npm run dev` serves the app on `localhost:5173` and is by far the fastest surface for layout work. But an action
app is an iframe with a conversation partner: `getTask()` asks Action Center for the task over `postMessage`, and
outside Action Center **nobody answers, so it rejects after three seconds** — `Timeout: Task data not received
from Action Center`. The scaffolded `useEffect` has no `.catch()`, so what you get is a blank shell and an
unhandled rejection in the console, which is indistinguishable from the app being broken.

So local dev needs one deliberate branch, and where you put it is the whole of the safety:

```ts
if (import.meta.env.DEV && new URLSearchParams(location.search).has('preview')) {
  const { previewTask } = await import('./dev/preview-task');  // dev-only, never bundled
  applyTask(previewTask);
  return;
}
applyTask(await codedActionAppService.getTask());              // the only path that ships
```

**One thing has to be fixed before any of this runs.** The scaffold puts
`export const entities = new Entities(sdk)` at **module scope** in `src/uipath.ts`. Outside Action Center the SDK
has no meta tags to read, so that constructor throws *at import time* — before your component mounts, and before
the `import.meta.env.DEV` branch can be taken. You get a blank shell and one `pageerror` reading *"Invalid SDK
instance"*, which looks exactly like the timeout above and is not. Guarding `getTask()` is not enough:
**build the services lazily**, a getter per service, or this whole loop is unreachable.

- **`import.meta.env.DEV` is what makes this safe.** `npm run build` substitutes `false`, so the branch and its
  dynamic import are eliminated — the fixture is not just unreachable in the deployed app, it is not in it. A
  query flag on its own does not achieve that; `spec.md` says why it has to.
- **Keep the `?preview` half as well.** Without it `npm run dev` never exercises the real path, and you stop
  noticing the day the real path breaks.
- **Before `getTask()`, never after it.** A fallback reached by something *failing* is the defect `spec.md` opens
  with. A branch taken before you ask is a different thing, and is fine.

**Capture the payload, do not invent one.** An invented fixture is a second contract that nothing else honours,
and an app tuned against it is tuned to a shape the platform never sends. Take the claim from the record and keep
it as it came:

```bash
uip df records get <entity-id> <record-id> --folder-key <seat-folder-key> --output json
```

For the task half you need only the identifiers in `contracts/review-task.md`. One trap: **do not capture from
`uip tasks get`** — it PascalCases every key in `Data` (*Find the waiting task*, below), so a fixture from it carries
`TriggerStage` where your app will be handed `triggerStage`.

Re-capture whenever the entity changes. A stale fixture is worse than no fixture: it is a green light for a shape
that nothing produces any more.

### Make a claim stop at the eligibility gateway

**You have to aim the run: a clean claim stops nowhere.** Both gateways are skipped when nothing is flagged
(`pdd.md` §4), so a randomly generated claim has a fair chance of closing itself before you can open anything.
`Retrieve Property Claim` takes `in_Scenario`, and `eligibility-fail` produces a claim the screening analysis
will flag:

```bash
uip or jobs start <process-key> --folder-key <your-seat-folder-key> \
  --input-arguments '{"in_ClaimID":"<claim-id>","in_Scenario":"eligibility-fail"}' --output json
```

For the second gateway use `review-fail`, which passes screening and is flagged by the analysis instead. The full
matrix is block 7's; two aimed runs are all this block needs.

**Start both of them at the top of the block, before you write any code.** A claim still has to walk the whole
case — extraction, screening, inspection, four analyses — before it reaches a gateway, so one aimed now is
waiting by the time you have a screen to point at it. Park several, aimed at different scenarios; it is cheaper
than editing rows to manufacture a state. (If your inspection wait is set to minutes rather than seconds, fix
that first — `5-case/cookbook.md` explains why it is free.)

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

### If you complete a task from the command line, hand the identifiers back

`uip tasks complete --data` **replaces** the whole payload with what you pass it. Send only the outputs and you
have erased the `inOut` values that let the task be re-opened — producing exactly the bug in `spec.md`'s
*A decided task must still open*, except you caused it from the terminal and the app gets the blame. Read the
task first, merge, then complete.

The same is true of every in-app write. There is more than one call site.

## Open it in a browser — in both states — before you call this done

**Every build so far reported this block finished on the strength of a clean TypeScript compile and a completed
task, and every one of them had an app that did not render.** A blank screen with a console error looks identical
to a working app from `uip tasks get`. So the last step is to look at it:

1. **A waiting task** — the app loads, the claim is on screen, both decisions are available.
2. **A completed task** — the app loads, shows what was decided, and offers nothing to press.

Neither may show an error screen, an empty page, or **anything in the console from *your app***. That
qualification matters: every Action Center task page emits console errors of its own — `orgId is invalid`, twice,
and a 404 on `tasksTenantMigration` — and they appear on the sign-in page too, before any app has loaded. Taken
literally the bar is unachievable, and an honest agent either reports failure on a working screen or learns to
ignore the console entirely.

**Open more than one claim, and open every tab.** The defect this step exists to catch is claim-dependent: the
screen opens, and the tab that dies is one click further in (`contracts/record-payloads.md`).

### Driving the browser when you have no browser

An action app has **no standalone surface**. It renders only at
`https://cloud.uipath.com/<org>/<tenant>/actions_/current-task/tasks/<taskId>`, which needs a real interactive
session — `uip login` does not help, and the coded-apps skill's Playwright script targets a *web* app on
localhost with its own sign-in button. A fresh Playwright profile lands on `account.uipath.com` and stops.

What works, in four points:

- `chromium.launchPersistentContext` with a **fixed `userDataDir`** and `headless: false`, the first time only.
- Navigate to the task URL and **have a human sign in once**. The profile persists, so every later capture is
  headless and unattended.
- **Poll until your app's own text appears in one of the frames** — not until the hostname is
  `cloud.uipath.com`. The hostname flickers back mid-redirect, and a naive check screenshots the login page.
- **Completing a task raises a confirmation dialog in the *parent* page** — *"Do you wish to mark this task as
  complete?"*, Complete / Cancel. `completeTask()` resolving is not the end of the flow, and a check that stops
  there records a decision that never happened.

A completed task decided *before* you fixed the payload rules can never render — its data was written at
completion and nothing rewrites it. Decide a fresh one and test against that.
