# Environment

Where you build, what already exists, and the names everything must agree on. Read *What already exists* before you design.

## Where you are building

| | |
|---|---|
| Environment | `https://cloud.uipath.com` — the portal: where you log in, where Studio Web and Action Center open |
| API host | SDK's `baseUrl` `https://api.uipath.com`. Anything a browser app calls goes here, never to the portal host. |
| Organization | `tpenlabs` |
| Tenant | `ClaimCaseWorkshop` |
| Your Orchestrator folder | `ClaimCase-<seat>` |

```bash
uip login status --output json     # confirm before anything else
```

**You share this tenant.** Prefix everything you create with your seat name.

**Your seat token is what follows `ClaimCase-` on your folder** — confirm it:

```bash
uip or folders list --all --limit 200 --output json --output-filter "[?starts_with(Name,'ClaimCase')].Name"
```

More than one result means you are seeing other people's. Yours is the one you were given.

## Toolchain — pinned

The CLI line decides which skills you get, and this seed was tested on exactly this one. Be on it before the first block:

| | |
|---|---|
| CLI line | `1.205` |
| Channel | `preview` |

```bash
uip config set version 1.205
uip config set updateChannel preview
uip update                      # the CLI and its tools move onto the line
uip skills install              # the skills follow it
uip --version                   # 1.205.x
```

A different line means different skills. If this line is ever found broken, this table changes — nothing else in the seed names a version.

**The line holds; the patch moves.** The first `uip` call of each day updates each tool within the line, and `uip update` refreshes the skills as well, so a long build can change patch under you. Do neither while a block is running; if a tool's behaviour changes mid-run, `uip --version` and `uip tools list` say what moved. To hold an exact build, `uip config set version <exact version>`.

## What already exists

**Deployed in your folder before you start. Bind them; never rebuild them.**

`PDD.md` §9 names six business systems. Five have an automation behind them and one does not:

| `PDD.md` §9 system | What is deployed | Read at |
|---|---|---|
| Claims Intake | `Retrieve Property Claim` | steps 1.1, 1.2 |
| Document Store | buckets `Claims` · `Insurance Policies Repository` · `Assessor Reports`, plus `Extract Claim Data (IXP)` and `Retrieve Inspection Report` | 1.2, 1.3, 3.1 |
| Policy Administration | `Retrieve Policy Document` | 1.4 |
| Claims History | `Retrieve Previous Claims` | 1.5 |
| Correspondence | `Client Notification` | 1.6, 6.3, 7.2 |
| **Settlements** | **nothing** | 6.2 |

**Read that last row twice.** Settlements is out of scope (`PDD.md` OS2) and nothing stands in for it: step 6.2 *records* the authorised amount and who approved it on the claim entity, and stops. **Do not design a settlement API, a payment call or an authorisation service** — it resolves to nothing at build time.

Likewise the claim entity is [yours to build](#the-claim-entity), not a service to call — there is no central record-writing component.

**An IXP project** is also provided: `property-claims-shared-45fcad56-ixp`, published and tagged `live`. Use it; you do not train a model.

**Their exact arguments, types and behaviour: [`contracts/provided-processes.md`](contracts/provided-processes.md).** Read it before binding anything.

## One name, everywhere

**One string, every surface — not a family of similar names.**

| Surface | Name |
|---|---|
| Orchestrator folder | `ClaimCase-Jane` |
| Local build folder | `Build/ClaimCase-Jane/` |
| Solution, and every package it publishes | `ClaimCase-Jane` |
| Deployment (`deploy run --name`) | `ClaimCase-Jane` — **exactly one, for the whole exercise** |
| Solution folder you deploy into | `ClaimCase-Jane-Deploy`, under your seat folder |
| **Claim record** | **`ClaimCase_Jane`** — underscore, not hyphen |
| **Coded Action App** | **`claim-review-jane`** — lower case; deployed into `ClaimCase-Jane`, the seat folder, not into `-Deploy` |
| **Coded Web App — the process app (block 6)** | **`property-claims-jane`** — lower case; deployed into `ClaimCase-Jane`, the seat folder, beside the Action App |
| Action task titles | `Eligibility review for Jane` · `Claim review for Jane` |
| Case name | `ClaimCase-Jane` |

Use the token exactly as it appears on your folder — `GPT01` is not `Gpt01`. **Two surfaces re-spell it and fail at create time on a message about the name:** the claim entity takes letters, digits and underscores and must start with a letter; the screen is lower case. Nowhere is it `ClaimCaseJane`. Task titles carry the seat because Action Center is one queue for the whole tenant.

## Deploying

**One solution, `Build/ClaimCase-<seat>/`, holding the case and the seven agents — `uip solution init` before the first project.** A case binds agents by name inside its own solution; never create a second solution for a component. **No app inside it, ever** — not scaffolded, not provisioned (`resources/` carries no `app` entry): an app packed inside deploys as a shell the case cannot raise a task against, and blocks redeploys once the standalone app is upgraded. The Coded Action App and the block-6 process app live beside the solution, each published and deployed by `uip codedapp` into your seat folder — `publish -t Action` for the Action App, then `deploy --folder-key <seat folder key>` — and the case binds the Action App by name with the seat folder as its `folderPath`.

**Redeploy in place — same name, higher version** (`3e-run/cookbook.md`, *Deploying*). A failed uninstall: `3e-run/cookbook.md`, *Deploying*. A `deploy run` that never installed leaves a record only the Orchestrator Solutions UI deletes; if the name is provably burnt — every verb refused, no non-final job in the folder — deploy once as `ClaimCase-<seat>-v2` and write down why, never a third name. Uninstall is recovery, not the loop: it deletes the solution folder, its key, the case process id and every running instance.

**Deploy into your seat folder** — `deploy run --parent-folder-path ClaimCase-<seat>`; without it the folder lands at the tenant root.

**A solution folder does not inherit its parent's buckets or processes** — anything calling a provided automation names `ClaimCase-<seat>` as its folder. `uip or processes list --folder-key <key>` at zero is the whole diagnosis.

## The claim entity

**Yours to build, in your seat folder** — create it with `--folder-key` of `ClaimCase-<seat>`; a tenant-level create is refused with *Missing permissions* or *You don't have permission to access the entity* — a scope you were never granted, not a broken login.

**The Data Fabric connection already exists and is shared** — `Shared Data Fabric Connection`, in the `Shared` folder. Do not create your own.

Schema: [`contracts/claim-entity.md`](contracts/claim-entity.md).

## The Coded Action App signs in through a shared registration

**One registration, shared by every seat; you cannot create another** (`external-apps create` → `403`).

| | |
|---|---|
| Name | `Claim Case External App` |
| **Client id** | **`24daf1c0-48be-4710-8d81-5467adfe7f15`** |
| Kind | Non-confidential — a public client, no secret, none to put in your code |
| Scopes | `DataFabric.Schema.Read` `DataFabric.Data.Read` `OR.Folders.Read` `OR.Buckets.Read` `OR.Jobs.Read` `OR.Users.Read` — and, for the process app of block 6, `OR.Tasks` `PIMS` `OR.Execution.Read` |

**Never run `external-apps update` on it.** It *replaces* the redirect list, so on a shared client it breaks everyone else's screen; deploy registers your redirect URL for you. **A coded-app skill may tell you to run `create` or `update` — do not**; that instruction is written for a client you own.

`uip codedapp deploy --client-id` registers `https://<org>.uipath.host/<app name>` once and reuses it on every redeploy. **`400 Failed to update external client redirect URI` means the shared list (100 URLs) is full** — tell the operator. Never deploy with `clientId: ""`, and never set `externalClientId` in a solution deploy config.

**User-scoped, and read-only towards the claim record** — the case writes it. The one write the registration allows is completing a task (`OR.Tasks`): block 6 decides through the gate task, and the case writes the record as it does from Action Center. `PIMS` and `OR.Execution.Read` read the case's stages (pre-aggregated counts and SLA roll-ups need Insights scopes it does not carry); `http://localhost:5173` is registered for local sign-in. `uipath.json`'s `scope` must match this list, never exceed it — `invalid_scope`, `401` or `403` on a listed scope is that file.

## Your machine

**Set this up before block 1.** Most lost hours on this exercise were the machine, not the build.

| | |
|---|---|
| A coding agent that sandboxes its shell | Exclude `uip` from the sandbox and call `uip` directly, never through a script that spawns it (a child process stays sandboxed). Claude Code: `"sandbox": {"excludedCommands": ["uip"]}` in `.claude/settings.local.json`. Inside a sandbox the CLI cannot write its token refresh and reports *refresh token invalid*: the login is fine, the sandbox blocked the write |
| Port `5173` | The only local sign-in redirect the shared registration knows (`6-process-app`). Keep it free: stop a dev server you started in `3f` before block 6 |

## Windows

The seat VM runs PowerShell, and **JSON on a command line is the largest time sink recorded on this exercise**: PowerShell rewrites quotes before `uip` sees them, and the error names the JSON rather than the shell.

| Issue | Fix |
|---|---|
| A command's JSON argument arrives mangled | **Prefer `--file` wherever a command offers it.** A here-string keeps `\u` escapes literally, and `node -e` quoting breaks the same way: write the JSON to a file. |
| The next command reports invalid JSON *at line 1 column 1*, or a byte `0xff` | PowerShell wrote the file. `Set-Content -Encoding utf8` and `Out-File -Encoding utf8` add a UTF-8 BOM (read with `encoding="utf-8-sig"`); `>` writes **UTF-16** (read with `encoding="utf-16"`; `utf-8-sig` does not fix it). Write files with Python, `open(path, "w", encoding="utf-8")` + `json.dump`, or from PowerShell with `[System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))`. |
| A checker crashes on `UnicodeEncodeError` | The console is cp1252. Run every Python script as `python -X utf8 …` on every call: `$env:PYTHONUTF8 = '1'` holds only in that one shell, and each tool call may be a new one. `python3` is a Store alias; use `python` or `py`. |
| Calling `uip` from a script fails or loses quotes | Call `node` on the CLI's entry script, one argv item per argument: `["node", "<npm root -g>/@uipath/cli/dist/index.js", *args]` (find the folder with `npm root -g`). `CreateProcess` cannot start `uip.cmd`, and the `uip.ps1` shim strips quotes out of a JSON argv element even when argv is a list. |
| `npm run dev -- --host` fails with *Unknown cli flags* | In PowerShell `npm` is `npm.ps1`, which drops the `--`. Use `npm.cmd run dev -- --host 127.0.0.1 --port 5173 --strictPort`, or `node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5173 --strictPort`. Keep `--strictPort`: without it Vite moves to `5174` and sign-in fails. |
