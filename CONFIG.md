# Build configuration

The values this build anchors on. Everything else you name yourself.

## Where you are building

| | |
|---|---|
| Environment | `https://cloud.uipath.com` |
| Organization | `tpenlabs` |
| Tenant | `CodingAgentsPractice` |
| Your folder | `ClaimCase-<seat>` — the Orchestrator folder assigned to you |

```bash
uip login status --output json     # confirm before anything else
```

**You share this tenant**, and not only with this workshop — other exercises publish here too. Prefix everything
you create — solution, processes, agents, entity, app — with your seat name so twenty builds can coexist. A
name without it is a collision waiting for the second participant to reach the same step.

**Your seat token is whatever follows `ClaimCase-` on your Orchestrator folder** — a number on some seats, a
name on others (`ClaimCase-04`, `ClaimCase-John`). Nothing in this folder states it, so confirm it rather than
assume:

```bash
uip or folders list --output json --output-filter "[?starts_with(Name,'ClaimCase')].Name"
```

If more than one comes back, the tenant is shared and you are seeing other people's — yours is the one whose
name you were given.

### One name, everywhere

**Your seat's name is `ClaimCase-<seat>`, and it is the same string in every surface.** Not a family of similar
names — the same one. It is what makes a folder, a package, a job and a log line attributable to you at a glance,
and it is what lets a teardown script find everything you made.

Written below with the seat token `Jane`; substitute your own.

| Surface | Name |
|---|---|
| Orchestrator folder | `ClaimCase-Jane` |
| Local build folder | `Build/ClaimCase-Jane/` |
| Solution, and every package it publishes | `ClaimCase-Jane` |
| **Deployment** (`deploy run --name`) | `ClaimCase-Jane` — **exactly one, for the whole exercise** |
| Solution folder you deploy into (`--folder-name`) | `ClaimCase-Jane-Deploy`, under your seat folder |
| IXP project, if you build your own | title it `ClaimCase-Jane` |
| **Data Fabric entity** | **`ClaimCase_Jane`** — underscore, not hyphen |
| **Coded app** | **`claim-review-jane`** — lower case, not hyphen-free |
| Action task titles | `Eligibility review for Jane` · `Claim review for Jane` |

The token is used **exactly as it appears on your folder** — `GPT01` is not `Gpt01`. **Two surfaces re-spell it
anyway, and both fail at create time on a message about the name rather than about the seat.**

- **The entity takes letters, digits and underscores only** and must start with a letter, so the hyphen that
  works everywhere else is rejected. Underscore there, hyphen everywhere else, and nowhere at all is it
  `ClaimCaseJane`.
- **A coded app name is lower case.** `claim-review-jane`, not `claim-review-Jane`.

Everything else is the token exactly as it appears on your folder.

**The task titles are not cosmetic.** Action Center is one queue for the whole tenant, so twenty rows all reading
*"Eligibility review"* cannot be told apart — and a reviewer opening the wrong seat's claim is a confusing five
minutes for two people. The title is set in the case plan, where the task is raised.

### One deployment, reused — never a name per attempt

**You redeploy many times. The deployment name never changes.** Uninstall the one you have, then deploy again
under the same name:

```bash
uip solution deploy uninstall ClaimCase-Jane --output json
uip solution deploy run --name ClaimCase-Jane --folder-name ClaimCase-Jane-Deploy \
  --parent-folder-path ClaimCase-Jane --package-name ClaimCase-Jane --package-version <v>
```

The tempting alternative — `-v103`, `-v104`, `-Run`, `-CaseRun2`, `-Block5` — is how one tenant reached **33
deployments for four seats**, each with its own folder and its own copy of every process. By the fifth attempt
nobody could say which one was running, and a `list` gives no clue: an uninstalled deployment stays in the
tenant's Solutions view forever.

The rule earns its keep at teardown. Because the name is derivable from the seat token and nothing else,
removing your work is one command that **cannot reach another seat's**. A name with an attempt suffix in it can
only be cleaned up by reading the list and guessing.

## Data Fabric: your entity is folder-scoped, the connection is shared

Two facts that decide how block 3 and block 5 are written. Neither is guessable and both fail late.

**Your claim entity lives in your seat folder, not at tenant level.** Create it with `--folder-key`, the key of
`ClaimCase-<seat>`. A tenant-level create is refused outright — `You don't have permission to access the entity,
field or record` — which reads like a broken login and is really a scope you were never granted. Folder scope is
also what gives you a space of your own: nobody else's build can see or touch your rows.

**The Data Fabric connection already exists and is shared.** `Shared Data Fabric Connection`, in the `Shared`
folder — do not create your own.

```bash
uip is connections list uipath-uipath-dataservice --refresh --all-folders --output json
```

The cost of folder scope lands in one place — the case's Data Fabric writes need the V3 activities rather than
the V2 ones the tooling reaches for by default. `5-case/cookbook.md` has the exact shape; it is six lines, and
it is the difference between a case that writes rows and one that faults with
`Entity 'ClaimCase_<seat>' not found at tenant level`.

## The reviewer's app signs in through a shared registration — do not create one

The screen you build in block 6 reads Data Fabric and Orchestrator on behalf of whoever is looking at it, and
that needs an OAuth client. **One already exists, it is shared by every seat, and you do not have permission to
make another.**

| | |
|---|---|
| Name | `Claim Case External App` |
| **Client id** | **`24daf1c0-48be-4710-8d81-5467adfe7f15`** |
| Kind | Non-confidential — a public client, no secret, and none to put in your code |
| Scopes | `DataFabric.Schema.Read` `DataFabric.Data.Read` `OR.Folders.Read` `OR.Buckets.Read` `OR.Jobs.Read` |

Put the client id and the scopes in your app's `uipath.json`, and pass the id again when you deploy:

```json
{
  "clientId": "24daf1c0-48be-4710-8d81-5467adfe7f15",
  "scope": "DataFabric.Schema.Read DataFabric.Data.Read OR.Folders.Read OR.Buckets.Read OR.Jobs.Read"
}
```

```bash
uip codedapp deploy -n claim-review-<seat> --client-id 24daf1c0-48be-4710-8d81-5467adfe7f15   --folder-key <your-seat-folder-key>
```

**Two Data Fabric resources exist on this tenant and only one of them works.** `DataFabricOpenApi` carries
`DataFabric.*`; `DataServiceOpenApi` carries `DataService.*` and is the older one. The TypeScript SDK calls
`/datafabric_/` and nothing else, so `DataService.*` buys you a token that authenticates perfectly and can read
no records at all. It fails as `Missing permissions: EntityRecords.View` — a *folder permission* message for what
is really a wrong-resource scope, which is why it sends people to check their folder roles for an afternoon
([findings 93](../../TestKitchen/findings.md)). Both pairs are registered on the shared client; request the
`DataFabric.*` pair.

Three things about it are worth knowing before you meet them as errors:

- **`uip admin external-apps create` will refuse you**, with `403`. That is not a broken login and not something
  to work around — managing OAuth clients is a tenant-wide administrative right and this exercise does not grant
  it. Use the id above.
- **The scopes are user scopes, not application scopes.** The token the app gets is bound to the person looking
  at the screen and can do nothing they could not do themselves. That is why one registration can be shared by
  twenty people safely.
- **They are read scopes only, deliberately.** The screen reads the claim record; the *case* writes it. If your
  design has the app writing to Data Fabric directly, that is the thing to change — the decision belongs on the
  record because a case task put it there, which is what makes it auditable.

`deploy` registers your app's own redirect URL against this registration for you. You never edit the
registration, and `uip admin external-apps update` would **replace** its redirect list rather than add to it —
which on a shared client means breaking everyone else's app.

## The reviewer's app is deployed to your seat folder, not your solution folder

`ClaimCase-<seat>`, the folder that holds your buckets and processes — **not** `ClaimCase-<seat>-Deploy`, the
one your solution deploys into.

A coded app is not part of the `.uipx` and does not travel with the solution, so nothing puts it there for you.
Publishing the same app name in two folder contexts made the platform register **two app identities** with the
same name on one seat; the tasks already raised stayed pinned to the first, every subsequent deploy upgraded the
second, and the app in Action Center stopped matching the app being fixed. It cost that seat an afternoon and it
is invisible until you compare an existing task's `AppId` against your own `.uipath/app.config.json`.

## One solution, one name, one place on disk

```
Build/ClaimCase-<seat>/             everything you generate — agents, the case, later the app
```

Not one solution per component. A case binds agents **by name inside its own solution**, so agents published in
a different solution are not reachable from the case that needs them — and every extra solution is another
package to version, deploy and uninstall in step. One solution, one deploy, one uninstall.

The names *inside* it are yours, with one rule: **anything visible at tenant level carries your seat name.**
`AGENTS.md` says where notes and documents go.

## What already exists — do not build these

Deployed in your folder before you start, and **ours rather than yours**: infrastructure so you spend your time
on the solution instead of on plumbing. You bind them; you never open them.

| | |
|---|---|
| Six processes | `Retrieve Property Claim` · `Extract Claim Data (IXP)` · `Retrieve Policy Document` · `Retrieve Previous Claims` · `Retrieve Inspection Report` · `Client Notification` |
| Buckets | `Claims` · `Insurance Policies Repository` · `Assessor Reports` |
| An IXP project | `property-claims-shared-45fcad56-ixp` — published, tagged `live`. Adopt it, or build your own (block 1 has a prompt for each). |

**Their arguments, types and behaviour are the contract in
[`contracts/provided-processes.md`](contracts/provided-processes.md)** — read it before binding anything in
block 5. Between them they cover every movement of a file or payload between storage and a task, so **if you are
about to build a bucket download, an IXP invocation or a PDF-to-text step, stop: it exists.**

No email connection is provisioned. `Client Notification` logs the letter rather than sending it, on purpose.

**Deploy into your seat folder, never the tenant root.** `solution deploy run` creates a folder, and without
`--parent-folder-path ClaimCase-<seat>` it creates it at the root — beside everyone else's, and outside the seat
that holds your processes and buckets.

**And a solution folder is not the same folder.** The sub-folder it creates does **not** inherit its parent's
buckets or processes. Anything in your case plan that calls one of the above needs
its folder named explicitly — `ClaimCase-<seat>`, your seat folder — or it resolves to an empty folder and fails at
run time. `uip or processes list --folder-key <key>` settles it in one call, and a count of zero is the whole
diagnosis.

## Model settings for the analysis agents

Pin these. They are not preferences — a model swap changes tool-call behaviour and has broken this build before.

| Setting | Value | Why |
|---|---|---|
| `temperature` | `0` | Same claim, same analysis. A reviewer comparing two runs of one claim must not see two answers. |
| `model` | `gpt-5.6-terra` | The default for this exercise. If you use another, **log it** (`log-finding.py`) — a model swap changes tool-call behaviour, so it belongs in the list of things you can rule out. |

## Say which agent you are, once

`log-finding.py` records `uip --version` and the seed version on every finding by itself. The one thing it
cannot know is what is driving it, so tell it once at the start of the session:

```bash
export WORKSHOP_AGENT="Codex"  WORKSHOP_MODEL="gpt-5.5"     # bash
$env:WORKSHOP_AGENT="Codex"; $env:WORKSHOP_MODEL="gpt-5.5"  # PowerShell
```

A green-then-red result is undiagnosable without them, and a model swap changes tool-call behaviour — it has
broken this build before.

## If you are on Windows

The seat VM runs PowerShell, and **the single largest time sink in the last run was JSON on a command line.**
PowerShell rewrites quotes before `uip` ever sees them, so an argument that prints correctly still arrives
mangled — and the error names the JSON, not the shell.

- **Prefer `--file` wherever a command offers it**, and write the file with UTF-8 **without a BOM**.
  `Set-Content -Encoding utf8` adds one, and the next command reports the file is not valid JSON *at line 1
  column 1* — which is the BOM, not your JSON. `python3 -c "..."` or `[IO.File]::WriteAllText()` write it clean.
- **Where only an inline argument exists** — `uip or jobs start --input-arguments` is the one you will meet —
  stop PowerShell from parsing at all:

  ```powershell
  uip.cmd --% or jobs start <guid> --input-arguments "{\"scenario\":\"auto-settle\",\"discrepancy\":\"\"}"
  ```

- `log-finding.py` already does the right thing; you never pass it JSON.

Two more that cost a retry each: `Get-Date -AsUTC` and `ConvertFrom-Json -Depth` do not exist in this
PowerShell. Use `[DateTime]::UtcNow.ToString('o')`, and parse large JSON with `python3` instead.
