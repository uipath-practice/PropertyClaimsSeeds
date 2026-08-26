# Environment

Where you build, what is already there, and the names everything has to agree on. Read *What already exists* before you design anything — it is the difference between binding a deployed automation and inventing a replacement for it.

## Contents

[Where you are building](#where-you-are-building) · [What already exists](#what-already-exists) · [One name, everywhere](#one-name-everywhere) · [Deploying](#deploying) · [The claim entity](#the-claim-record) · [The validation app signs in through a shared registration](#the-reviewers-screen-signs-in-through-a-shared-registration) · [Model settings](#model-settings) · [Windows](#windows)

## Where you are building

| | |
|---|---|
| Environment | `https://cloud.uipath.com` |
| Organization | `tpenlabs` |
| Tenant | `CodingAgentsPractice` |
| Your Orchestrator folder | `ClaimCase-<seat>` |

```bash
uip login status --output json     # confirm before anything else
```

**You share this tenant, and not only with this workshop.** Prefix everything you create with your seat name, or twenty builds collide.

**Your seat token is whatever follows `ClaimCase-` on your folder** — a number on some seats, a name on others. Nothing here states it, so confirm rather than assume:

```bash
uip or folders list --output json --output-filter "[?starts_with(Name,'ClaimCase')].Name"
```

More than one result means you are seeing other people's. Yours is the one you were given.

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

The same warning applies to the claim entity itself: `PDD.md` §1.5 P5 asks for a store, and it is [yours to build](#the-claim-record), not a service to call. A design that routes every write through a central record-writing component is designing a component that does not exist.

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
| **Validation app** | **`claim-review-jane`** — lower case |
| Action task titles | `Eligibility review for Jane` · `Claim review for Jane` |
| Case name | `ClaimCase-Jane` |

Use the token exactly as it appears on your folder — `GPT01` is not `Gpt01`. **Two surfaces re-spell it and both fail at create time on a message about the name rather than about the seat:** the claim entity takes letters, digits and underscores only and must start with a letter; the screen is lower case. Nowhere is it `ClaimCaseJane`.

**Task titles are not cosmetic.** Action Center is one queue for the whole tenant, so twenty rows reading *"Eligibility review"* cannot be told apart, and a reviewer opening the wrong seat's claim is a confusing five minutes for two people.

## Deploying

**One solution, holding everything.** A case binds agents by name **inside its own solution**, so an agent published elsewhere is unreachable from the case that needs it. Never create a second solution for a component, however tidy it looks.

**Redeploy in place. The name never changes** — same name, higher package version. Uninstall is the recovery path, not the loop: it deletes the solution folder, taking the folder key, the case process id and every running instance with it.

**Deploy into your seat folder, never the tenant root.** Without `--parent-folder-path ClaimCase-<seat>`, `deploy run` creates the folder at the root, beside everyone else's.

**A solution folder is not the same folder.** The sub-folder it creates does **not** inherit its parent's buckets or processes, so anything calling one of the automations above needs its folder named explicitly — `ClaimCase-<seat>` — or it resolves to an empty folder and fails at run time. `uip or processes list --folder-key <key>` settles it in one call, and a count of zero is the whole diagnosis.

## The claim entity

**Yours to build, in your seat folder, not at tenant level.** Create it with `--folder-key`, the key of `ClaimCase-<seat>`. A tenant-level create is refused with *"You don't have permission to access the entity, field or record"*, which reads like a broken login and is really a scope you were never granted. Folder scope is also what gives you a space of your own.

**The Data Fabric connection already exists and is shared** — `Shared Data Fabric Connection`, in the `Shared` folder. Do not create your own.

Its schema is pinned in [`contracts/claim-entity.md`](contracts/claim-entity.md), and that file says why it is pinned rather than designed.

## The validation app signs in through a shared registration

**One registration exists, it is shared by every seat, and you cannot make another** — `uip admin external-apps create` returns `403`, because managing OAuth clients is a tenant-wide administrative right this exercise does not grant.

| | |
|---|---|
| Name | `Claim Case External App` |
| **Client id** | **`24daf1c0-48be-4710-8d81-5467adfe7f15`** |
| Kind | Non-confidential — a public client, no secret, none to put in your code |
| Scopes | `DataFabric.Schema.Read` `DataFabric.Data.Read` `OR.Folders.Read` `OR.Buckets.Read` `OR.Jobs.Read` `OR.Users.Read` |

**Never run `external-apps update` on it.** It *replaces* the redirect list rather than adding to it, so on a shared client it breaks everyone else's screen. Deploy registers your own redirect URL for you. **A coded-app skill may instruct you to run `create` or `update` on its own authority — do not**; that instruction is written for a client you own.

**The scopes are read-only and user-scoped**, deliberately. The screen reads the claim entity; the *case* writes it. If your design has the screen writing directly, that is the thing to change — a decision belongs on the record because a case task put it there, which is what makes it auditable.

## Model settings

Pin these. They are not preferences.

| Setting | Value | Why |
|---|---|---|
| `temperature` | `0` | Same claim, same answer. A reviewer comparing two runs of one claim must not see two results. |
| `model` | `gpt-5.6-terra` | The default. Use another and **log it** — a model swap changes tool-call behaviour, so it belongs in the list of things you can rule out. |

## Windows

The seat VM runs PowerShell, and **JSON on a command line is the single largest time sink recorded on this exercise.** PowerShell rewrites quotes before `uip` sees them, so an argument that prints correctly still arrives mangled, and the error names the JSON rather than the shell.

- **Prefer `--file` wherever a command offers it**, written UTF-8 **without a BOM**. `Set-Content -Encoding utf8` adds one, and the next command reports invalid JSON *at line 1 column 1* — that is the BOM, not your JSON.
- **Calling `uip` from a script? Call `node` directly.** Driving the installed `uip.ps1` shim from Python's `subprocess` strips quotes out of a JSON argv element even when argv is a list.
