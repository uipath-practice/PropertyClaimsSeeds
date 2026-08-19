# Build configuration

The values this build anchors on. Everything else you name yourself.

## Where you are building

| | |
|---|---|
| Environment | `https://cloud.uipath.com` |
| Organization | `tpenlabs` |
| Tenant | `CodingAgentsPractice` |
| Your folder | `ClaimCase-<NN>` — the Orchestrator folder assigned to you |

```bash
uip login status --output json     # confirm before anything else
```

**You share this tenant**, and not only with this workshop — other exercises publish here too. Prefix everything
you create — solution, processes, agents, entity, app — with your seat number so twenty builds can coexist. Data
Fabric entity names in particular are **tenant-scoped**, so an unprefixed `ClaimCase` collides with someone
else's on the first deploy.

**Your seat number is the `NN` in your Orchestrator folder**, and nothing in this folder states it — confirm it
rather than assume:

```bash
uip or folders list --output json --output-filter "[?starts_with(Name,'ClaimCase')].Name"
```

**The entity name is the strict one.** Data Fabric takes letters, digits and underscores only, and the name must
start with a letter — so your folder is `ClaimCase-07` and your entity is **`ClaimCase_07`**. The hyphen that
works everywhere else is rejected there, and it is rejected at create time with a message about the name rather
than about the seat, which is why it is worth knowing before you meet it.

## One solution, one name, one place on disk

```
Build/ClaimCase<NN>/             everything you generate — agents, the case, later the app
```

Not one solution per component. A case binds agents **by name inside its own solution**, so agents published in
a different solution are not reachable from the case that needs them — and every extra solution is another
package to version, deploy and uninstall in step. One solution, one deploy, one uninstall.

The names *inside* it are yours, with one rule: **anything visible at tenant level carries your seat number.**
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

**You create the Data Fabric connection yourself** in block 3 — it has to be owned by you.

**A solution folder is not the same folder.** Deploying a solution creates a sub-folder, and a sub-folder does
**not** inherit its parent's buckets or processes. Anything in your case plan that calls one of the above needs
its folder named explicitly — `ClaimCase-<NN>`, your seat folder — or it resolves to an empty folder and fails at
run time. `uip or processes list --folder-key <key>` settles it in one call, and a count of zero is the whole
diagnosis.

## Model settings for the analysis agents

Pin these. They are not preferences — a model swap changes tool-call behaviour and has broken this build before.

| Setting | Value | Why |
|---|---|---|
| `temperature` | `0` | Same claim, same analysis. A reviewer comparing two runs of one claim must not see two answers. |
| `model` | `gpt-5.6-terra` | The default for this exercise. If you use another, **record which** in `build-findings.md` — a model swap changes tool-call behaviour, so it belongs in the list of things you can rule out. |

## Versions to record

`uip` self-updates, and the UiPath skills change often. When something works and then stops, the version is the
first suspect and the only one you cannot reconstruct afterwards. Note these in `build-findings.md` at the start:

```bash
uip --version
```

Plus your coding agent and model. A green-then-red result is undiagnosable without them.
