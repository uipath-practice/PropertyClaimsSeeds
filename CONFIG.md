# Environment

Where you build, what is already there, and the names everything has to agree on. Read *What already exists* before you design anything — it is the difference between binding a deployed automation and inventing a replacement for it.

## Contents

[Where you are building](#where-you-are-building) · [Toolchain](#toolchain--pinned) · [What already exists](#what-already-exists) · [One name, everywhere](#one-name-everywhere) · [Deploying](#deploying) · [The claim entity](#the-claim-entity) · [The Coded Action App signs in through a shared registration](#the-coded-action-app-signs-in-through-a-shared-registration) · [Windows](#windows)

## Where you are building

| | |
|---|---|
| Environment | `https://cloud.uipath.com` — the portal: where you log in, where Studio Web and Action Center open |
| API host | SDK's `baseUrl` `https://api.uipath.com`. Anything a browser app calls goes here, never to the portal host.  |
| Organization | `tpenlabs` |
| Tenant | `CodingAgentsPractice` |
| Your Orchestrator folder | `ClaimCase-<seat>` |

```bash
uip login status --output json     # confirm before anything else
```

**You share this tenant.** Prefix everything you create with your seat name, or twenty builds collide.

**Your seat token is whatever follows `ClaimCase-` on your folder** — a number or name. Nothing here states it, so confirm rather than assume:

```bash
uip or folders list --all --limit 200 --output json --output-filter "[?starts_with(Name,'ClaimCase')].Name"   # --all and an explicit --limit, or the CLI refuses
```

More than one result means you are seeing other people's. Yours is the one you were given.

## Toolchain — pinned

**The CLI line decides which skills you get** — `uip skills install` takes the newest skills on the CLI's own `major.minor` line — and this seed is tested on exactly one line before every session. Be on it before the first block:

| | |
|---|---|
| CLI line | `1.201` |
| Channel | `preview` |

```bash
uip config set version 1.201
uip config set updateChannel preview
uip update                      # the CLI and its tools move onto the line
uip skills install              # the skills follow it
uip --version                   # 1.201.x
```

A different line means different skills and a seed written for another one. If this line is ever found broken, this table changes — nothing else in the seed names a version.

## What already exists

**Deployed in your folder before you start. Bind them; never rebuild them.** They are the integration layer — in a real insurer, fetching a policy means driving a portal; here it is a storage bucket behind the same interface. What that leaves you is the part worth practising.

`PDD.md` §9 names six business systems. Five have an automation behind them and one does not:

| `PDD.md` §9 system | What is deployed | Read at |
|---|---|---|
| Claims Intake | `Retrieve Property Claim` | steps 1.1, 1.2 |
| Document Store | buckets `Claims` · `Insurance Policies Repository` · `Assessor Reports`, plus `Extract Claim Data (IXP)` and `Retrieve Inspection Report` | 1.2, 1.3, 3.1 |
| Policy Administration | `Retrieve Policy Document` | 1.4 |
| Claims History | `Retrieve Previous Claims` | 1.5 |
| Correspondence | `Client Notification` | 1.6, 6.3, 7.2 |
| **Settlements** | **nothing** | 6.2 |

**That last row is the one to read twice.** Settlements is out of scope for automation (`PDD.md` OS2) and no automation stands in for it. Step 6.2 *records* the authorised amount and who approved it on the claim entity, and stops. **Do not design a settlement API, a payment call or an authorisation service** — two independent designs of this process invented one, and it resolved to nothing at build time.

The same warning applies to the claim entity itself: `PDD.md` §1.5 P5 asks for a store, and it is [yours to build](#the-claim-entity), not a service to call. A design that routes every write through a central record-writing component is designing a component that does not exist.

**An IXP project** is also provided: `property-claims-shared-45fcad56-ixp`, published and tagged `live`. Adopt it, or train your own.

**Their exact arguments, types and behaviour are [`contracts/provided-processes.md`](contracts/provided-processes.md).** Read it before binding anything.

**No email connection is provisioned.** `Client Notification` logs the letter rather than sending it, on purpose. No letter ever reaches anyone.

## One name, everywhere

**One string, every surface — not a family of similar names.** It is what makes a folder, a package, a job and a log line attributable to you at a glance, and what lets a teardown find everything you made.

| Surface | Name |
|---|---|
| Orchestrator folder | `ClaimCase-Jane` |
| Local build folder | `Build/ClaimCase-Jane/` |
| Solution, and every package it publishes | `ClaimCase-Jane` |
| Deployment (`deploy run --name`) | `ClaimCase-Jane` — **exactly one, for the whole exercise** |
| Solution folder you deploy into | `ClaimCase-Jane-Deploy`, under your seat folder |
| IXP project, if you train your own | `ClaimCase-Jane` |
| **Claim record** | **`ClaimCase_Jane`** — underscore, not hyphen |
| **Coded Action App** | **`claim-review-jane`** — lower case; deployed into `ClaimCase-Jane`, the seat folder, not into `-Deploy` |
| Action task titles | `Eligibility review for Jane` · `Claim review for Jane` |
| Case name | `ClaimCase-Jane` |

Use the token exactly as it appears on your folder — `GPT01` is not `Gpt01`. **Two surfaces re-spell it and both fail at create time on a message about the name rather than about the seat:** the claim entity takes letters, digits and underscores only and must start with a letter; the screen is lower case. Nowhere is it `ClaimCaseJane`.

**Task titles are not cosmetic.** Action Center is one queue for the whole tenant, so twenty rows reading *"Eligibility review"* cannot be told apart, and a reviewer opening the wrong seat's claim is a confusing five minutes for two people.

## Deploying

**One solution, holding the Maestro case and the seven Agents — created before the first project.** `uip solution init` at `Build/ClaimCase-<seat>/`, then every Agent and the case are scaffolded inside it; the Coded Action App is the one thing that lives beside it (below). A case binds agents by name **inside its own solution**, so an agent published elsewhere is unreachable from the case that needs it. Never create a second solution for a component, however tidy it looks. **The Coded Action App is the one exception**: it lives beside the solution and is deployed by its own command into your seat folder — `uip codedapp publish -t Action`, then `uip codedapp deploy --folder-key <your seat folder>` — and the case binds it by name with that folder as its `folderPath`. Measured 2026-08-27: an app packed inside the solution deploys as a shell the case cannot raise a task against.

**Redeploy in place. The name never changes** — same name, higher package version; the verbs, the poll and the one trap are the first row of `3e-run/cookbook.md`, *Deploying*. **A failed uninstall is a job that is not final** — stop it and uninstall again (`known-issues/cli-commands.md`, *`deploy uninstall` fails with `Validation failed.`*); a successful uninstall frees the name. **One escape, once:** a `deploy run` that never installed leaves a record the CLI cannot remove, and only the Orchestrator Solutions UI deletes it. If the pinned name is provably burnt (every verb refused, no non-final job in the folder), deploy as `ClaimCase-<seat>-v2` and write down why; never a third name. Uninstall is the recovery path, not the loop: it deletes the solution folder, taking the folder key, the case process id and every running instance with it.

**Deploy into your seat folder, never the tenant root.** Without `--parent-folder-path ClaimCase-<seat>`, `deploy run` creates the folder at the root, beside everyone else's.

**A solution folder is not the same folder.** The sub-folder it creates does **not** inherit its parent's buckets or processes, so anything calling one of the automations above needs its folder named explicitly — `ClaimCase-<seat>` — or it resolves to an empty folder and fails at run time. `uip or processes list --folder-key <key>` settles it in one call, and a count of zero is the whole diagnosis.

## The claim entity

**Yours to build, in your seat folder, not at tenant level.** Create it with `--folder-key`, the key of `ClaimCase-<seat>`. A tenant-level create is refused with *"You don't have permission to access the entity, field or record"*, which reads like a broken login and is really a scope you were never granted. Folder scope is also what gives you a space of your own.

**The Data Fabric connection already exists and is shared** — `Shared Data Fabric Connection`, in the `Shared` folder. Do not create your own.

Its schema is pinned in [`contracts/claim-entity.md`](contracts/claim-entity.md), and that file says why it is pinned rather than designed.

## The Coded Action App signs in through a shared registration

**One registration exists, it is shared by every seat, and you cannot make another** — `uip admin external-apps create` returns `403`, because managing OAuth clients is a tenant-wide administrative right this exercise does not grant.

| | |
|---|---|
| Name | `Claim Case External App` |
| **Client id** | **`24daf1c0-48be-4710-8d81-5467adfe7f15`** |
| Kind | Non-confidential — a public client, no secret, none to put in your code |
| Scopes | `DataFabric.Schema.Read` `DataFabric.Data.Read` `OR.Folders.Read` `OR.Buckets.Read` `OR.Jobs.Read` `OR.Users.Read` |

**Never run `external-apps update` on it.** It *replaces* the redirect list rather than adding to it, so on a shared client it breaks everyone else's screen. Deploy registers your own redirect URL for you. **A coded-app skill may instruct you to run `create` or `update` on its own authority — do not**; that instruction is written for a client you own.

**The redirect list holds 100 URLs and every seat spends one.** `uip codedapp deploy --client-id` registers `https://<org>.uipath.host/claim-review-<seat>` once and reuses it on every redeploy. **`400 Failed to update external client redirect URI` means the list is full** — nothing about your app is wrong; tell the operator (`infra/provisioning/reset/prune-redirects.sh` frees it) rather than deploying with `clientId: ""` — that leaves the platform's meta tags empty, your code's fallback config silently takes over, and a portal URL typed into it produced a phantom CORS wall that cost a block (`3f-validation/cookbook.md`). Never set `externalClientId` in a solution deploy config: each such deploy appends an anonymous `action-<id>` URL, which is how 86 dead entries filled the list on 2026-08-27 (`known-issues/cli-commands.md`).

**The scopes are read-only and user-scoped**, deliberately. The Action App reads the claim entity; the *case* writes it. If your design has the app writing directly, that is the thing to change — a decision belongs on the record because a case task put it there, which is what makes it auditable.

## Windows

The seat VM runs PowerShell, and **JSON on a command line is the single largest time sink recorded on this exercise.** PowerShell rewrites quotes before `uip` sees them, so an argument that prints correctly still arrives mangled, and the error names the JSON rather than the shell.

- **Prefer `--file` wherever a command offers it**, written UTF-8 **without a BOM**. `Set-Content -Encoding utf8` adds one, and the next command reports invalid JSON *at line 1 column 1* — that is the BOM, not your JSON.
- **Calling `uip` from a script? Call `node` directly.** Driving the installed `uip.ps1` shim from Python's `subprocess` strips quotes out of a JSON argv element even when argv is a list.
