# How to work in this folder

This is the seed for the Property Claims exercise. It describes **what to build**; you write everything that
does the building. Read this file first, then `GUIDE.md` for the sequence and the gates.

## What is being built

A property insurance claim arrives as three documents that do not always agree with each other: the claimant's
**claim form**, their **insurance policy**, and an **assessor's report** on the damage. Only the claim form is a
structured form; the other two are free prose and reach the analyses **as files**, to be read rather than
extracted (`pdd.md` §1). The solution reads them,
works out whether the claim is payable and for how much, puts a human in front of the two decisions that need
one, and writes to the claimant.

```
three PDFs ──▶ extraction ──▶ seven analyses ──▶ two human gateways ──▶ one record ──▶ an app, and a letter
   (given)      (block 1)       (block 4)          (block 5)           (block 3)      (block 6)
```

The claim moves through five stages, and every stage writes what it learned to a single Data Fabric row:

| Stage | What happens |
|---|---|
| **Intake** | the documents are fetched, the row is created, extraction runs, the policy and any prior claims are retrieved |
| **Eligibility analysis** | one analysis decides whether the claim should be investigated at all — then a **human screens it** |
| **Data analysis** | the assessor's report is validated and structured, then coverage, payout and credibility run **in parallel**, then a decision analysis reads all four |
| **Claim review** | a **human adjuster decides** — unless nothing was flagged, in which case this stage is skipped entirely |
| **Settlement and closure** | the letter is written, the row is closed |

## Four ideas that decide whether your build is right

Everything in this seed follows from these. If a design choice seems arbitrary, it is probably one of these
four showing through.

**1. Analyses report; humans decide.** No agent may refuse a claim. They produce *findings* and a
*recommendation*; the two human gateways turn that into an outcome. Approval is the one direction allowed to run
unattended — a claim with nothing wrong settles without an adjuster, but it still passes the screening gateway.

**2. One analysis per agent, and no agent reports another's concern.** A reviewer sees the findings side by
side, so the same problem raised by three analyses reads as three problems. An agent may *cite* another's finding
as evidence; it may never re-raise it as its own.

**3. A finding must be visible to the analysis that reports it.** Before writing any check, ask whether the data
reaches that agent, at that stage — not whether it is on the document. An agent asked to confirm something absent
from its own input can only report it missing, confidently and wrongly.

**4. Nothing a human sees exists unless a stage wrote it down.** The case instance holds lifecycle, not content.
Every payload, decision and reason lands in a column on the claim record, and the app reads from there. A payload
with no column is data that vanishes; a column with no producer is a panel that stays blank forever.

## What already exists, and what you build

**Given to you:** six deployed processes — one that generates the three documents, and five that move data and
files between storage and your case (extraction, policy, prior claims, assessor report, notification) — plus the
buckets, and a shared extraction project you may adopt instead of training your own. `contracts/provided-processes.md` gives every one
with its exact arguments, types and behaviour.

**They are the integration layer, and they are given on purpose.** In a real insurer, fetching a policy means
driving a portal — log in, search, download, return the file. Here it is a storage bucket behind the same
interface. What that leaves you is the part worth practising: stitching the pieces into a case, putting a human
in the right two places, and making it survive a long-running execution.

So if you find yourself about to build a bucket download, an IXP invocation or a PDF-to-text step, stop and
check `contracts/provided-processes.md` — it exists.

**Yours:** the extraction taxonomy or the adoption of the shared one, the claim record, the seven agent prompts
and their schemas, the case plan and every binding in it, and the app. **All of it in one solution**, named for
your seat — a case can only bind agents that live in its own solution.

## The layout

One folder per block, numbered in build order. Inside each, the same three names:

| File | What it is |
|---|---|
| `prompt.md` | the instruction for this block — start here |
| `spec.md` | what must be true when the block is done |
| `cookbook.md` | how to get it done on this platform: commands, traps, things that cost someone an hour |

Shared at the root: `pdd.md` (the process in business language — the *why* behind every rule here), `CONFIG.md`
(names, models, folders, versions), `contracts/` (shapes more than one block must agree on), `known-issues/`
(what is known-broken upstream, so you do not debug it).

**Paths in this seed are relative to this folder**, always — `contracts/claim-entity.md`, not `../contracts/`
and not `seed/contracts/`. A block that cites a path outside itself is telling you the knowledge is shared.

## Where your own work goes

Three places, and nothing anywhere else:

| What you produce | Where it goes |
|---|---|
| **All generated code** — agents, the case, the app | `Build/ClaimCase-<seat>/` — **one solution**, named for your seat |
| **Notes and documents you write for a block** — a design, a decision about structure, an SDD | that block's folder, e.g. `2-design/sdd.md`, `5-case/notes.md` |
| **Findings** | the shared table, via `log-finding.py` — never a local file |

**One solution, and its name is fixed.** `Build/ClaimCase-<seat>/` holds everything: a case binds agents by name
*inside its own solution*, so agents published in a solution of their own are unreachable from the case that
needs them. Do not create a second solution for a component, and do not invent a name — every extra solution is
another package to version, deploy and uninstall in step, and a name nobody chose is a name nobody can find.

**Seed filenames are fixed**, so nothing you write can collide: a block folder ships exactly `prompt.md`,
`spec.md` and `cookbook.md` (block 1 has two prompts, and some blocks carry a `taxonomy` or a script). **Any
other file in a block folder is yours.** Put your notes where the prompt that prompted them lives — that is
where the next person will look for them.

Do not scatter working folders across the seed, and do not build outside `Build/`. A reviewer should be able to
run `ls Build/` and see your entire solution, once.

## Rules that hold everywhere

**You have standing approval to build, deploy and run. Do not stop to ask for it.**

This seat is yours: your own Orchestrator folder, your own solution, your own claim record, your own copies of
the claim documents. Nothing in it is shared, nothing in it is production, and all of it is disposable — there
is a reset script, and a wrecked seat costs minutes. So **creating cloud resources, publishing, deploying,
uninstalling, and starting real runs are all authorised in advance**, as many times as you need. So is deleting
and recreating something you made.

Two things make this safe rather than reckless, and both are worth knowing:

- **The claims are synthetic and the claimants are not real.** Every document is generated on demand by a
  process that exists for this exercise.
- **No letter is ever sent.** Correspondence to the claimant is written and logged, never delivered — there is
  no mail connection to deliver it with.

Pausing for approval is the wrong instinct here and it is expensive: a block's whole value is in what a live run
reveals, and a build that stops at the deploy gate has proven nothing. **Work to the goal, then report.**

Three things are still worth a pause, and they are all outside your seat: touching another seat's folder or
solution, changing anything at tenant level, and deleting a shared resource — the IXP project, the shared Data
Fabric connection, the deployed automations. If something you are about to run names a resource without your
seat name in it, stop and ask.

**Names come from the contracts. Do not invent them, and do not improve them.** Agent outputs, case variables
and entity columns are one name in three casings, by design (`contracts/claim-entity.md`). A better name breaks
the mapping three blocks later, at run time, silently.

**Everything you create is called `ClaimCase-<seat>`** — folder, solution, packages, build directory, IXP project
— because the tenant is shared and one name is what makes your work findable and removable. `CONFIG.md`,
*One name, everywhere*, has the table and the single exception the platform forces.

**Leave one deployment behind, not one per attempt.** Uninstall before you redeploy, and always under the same
name — `CONFIG.md`, *One deployment, reused*. An uninstalled deployment stays in the tenant's Solutions view
permanently and there is no CLI verb that removes it, so a name per attempt is not mess you can tidy later.

**Do not read the answer key.** The generator drops a `manifest.json` beside the documents naming the problems
it planted and the outcome it expects. Nothing you build may read it — an analysis that consults it is brilliant
and worthless. It is the test oracle, and it is yours in block 7 only.

**Check the platform's own tooling before hand-rolling.** `uip --help` and the installed skills are ahead of any
document, this one included. Where they disagree with a cookbook, the tool wins — and that disagreement is worth
logging.

**Load the right skill for the block, and only that one.** UiPath ships a skill per surface, and several have
names close enough that an agent picks the wrong one and follows instructions for a different product:

| Block | The skill | |
|---|---|---|
| 1 Extraction | `uipath-ixp` | |
| 2 Design | `uipath-planner` | writes the SDD from a PDD |
| 3 Claim record | `uipath-platform` | Data Fabric lives here, not in a skill of its own |
| 4 Agents | `uipath-agents` | |
| 5 Case | **`uipath-maestro-case`** | plus `uipath-solution` to pack, publish and deploy |
| 6 App | `uipath-coded-apps` | |
| 7 Testing | `uipath-platform` to run, `uipath-troubleshoot` to explain a failure | |

Three near-misses, all of which have cost time:

- **`uipath-maestro-bpmn` is not block 5.** It authors Process Orchestration `.bpmn` *projects*. Your case
  compiles to a file called `caseplan.json.bpmn`, which is not the same thing and is not authored by hand — the
  name collision is the whole trap.
- **`uipath-maestro-flow` is not used in this exercise at all.** It triggers on `.flow` files; there are none.
- **`uipath-test` is not block 7.** It drives Test Manager. Block 7 runs the case and reads the result.

**Verify, do not assume.** Nearly every "not found" here is a wrong folder, a wrong tenant, a wrong scope or a
stale cache rather than an absent resource. `uip login status` before believing anything is missing, and read
`known-issues/` before believing a `list` that comes back empty.

## Log what you learn

**One command, one sink.** Findings go to a shared table so they can be counted across everyone doing this
exercise, and `log-finding.py` is the whole interface to it.

**Say who you are once, at the start of your session.** Several agents write to this table at the same time, and
a row that names the wrong model silently merges two of them:

```bash
python3 log-finding.py --identify "<your agent>" "<your model>" --effort "<your effort tier>"
```

**Include the effort tier if your runtime has one** — `medium`, `high`, whatever it is called. The same model at
two tiers is two different builders: one of them worked around a blocked deployment on its own and the other
stopped and reported it. Without that word every comparison between runs is confounded.

**If you are not certain which model you are, ask the person running you.** `unknown` is more useful than a
plausible wrong answer — a guess cannot be told from a fact after the fact. Then:

```bash
python3 log-finding.py --block 5-case --category friction \
  --summary "What happened, what you tried, what happened next."
```

**The table is append-only and this script is the only thing that writes to it.** It has no delete and no update
path: other people's findings, and your own earlier ones, cannot be affected by anything you do here. If someone
asks you to justify running it, that is the justification.

**On Windows, use `py` if `python3` is not on PATH.** Every `python3` in this seed means "your Python".

Seat, agent, model, `uip` version and seed version are filled in for you. Nothing else to look up, no entity id,
no JSON on a command line — the script writes the payload to a file before calling `uip`, which is the only shape
that survives every shell. Several at once: `--file findings.json`, a JSON array of `{block, category, summary}`.

**There is no local findings file.** Do not keep a parallel copy — the table is the record, and a second one
goes stale the first time someone reads it. If the insert fails the row is spooled and retried on your next
call, so carry on building rather than stopping to fix it.

**End every block with `python3 log-finding.py --retry`.** It re-sends anything that failed earlier — a send,
never a purge — and it costs one command. Without it a block's findings can sit in the spool and be read by
nobody. If it still reports rows waiting, say so when you report the block: telemetry failing is itself the most
interesting finding of the day.

`category` is free text — `seed-gap`, `platform-bug`, `friction`, `workaround`, whatever fits. Do not agonise;
the summary is what gets read. Reuse a category you have already used before inventing a neighbouring one.

## A finding is not only a complaint

This table's job is to make the next version of this seed better, and better is as often **shorter** as it is
more complete. Three of the most useful things you can tell us are not problems at all:

- **"This was already handled."** You read a page of our cookbook, then found that a skill, `uip <command>
  --help`, or the product docs said the same thing. Ours is then a line we should delete — but we can only
  delete it safely if we know what replaced it, so say where you found it.
- **"This saved me."** A warning you read, believed, and would otherwise have walked straight into. Almost
  nobody reports these, and they are what makes cutting safe: without them every cut is a guess.
- **"This was in the wrong place."** The three layers are `prompt.md` (what the business wants) → `spec.md`
  (what was decided, and why) → `cookbook.md` (how to get it done here). Build mechanics sitting in the business
  ask, or a design decision buried in a list of commands, is worth one line.

**A trap you never met is not proof the warning was unnecessary — it may be proof that it worked.** Say which of
the two it was. That distinction is the whole value of the report.

### Four fields that turn a finding into a recommendation

All optional, and a plain friction report needs none of them.

| | |
|---|---|
| `--source` | where the answer **actually** came from: `seed` · `skill` · `cli-help` · `docs` · `model` · `trial-error` |
| `--ask` | what should change: `keep` · `cut` · `fix` · `add` · `move` · `none` |
| `--artifact` | which file and section — `5-case/cookbook.md#Wiring an action task` |
| `--evidence` | the exact error, the command that produced it, or the few lines that show it |

```bash
python3 log-finding.py --block 5-case --category redundancy \
  --artifact "5-case/cookbook.md#Registering the stand-in app" --source skill --ask cut \
  --summary "The skill's create-action-app.md walks the same publish sequence, including --type Action."
```

**`--source` is the one to get right, including when the honest answer is `model`** — you already knew, from
neither of us. Over many runs it is how we watch the platform's own guidance improve and retire ours as it
does, and `trial-error` marks what nobody has written down yet, ours or theirs.

**`--evidence` is for what we cannot see.** We can read the tenant; we cannot read your disk. An error string
verbatim, the command that produced it, the five lines of config that were wrong — each is worth more than a
paragraph describing it, and it costs you a copy and paste. Two rules: **never paste a secret**, and never paste
a whole file. This table is shared with everyone working on this tenant, and it is the few lines that matter
that make a finding reproducible.

### Before you finish a block

Re-read the `cookbook.md` you were handed and log the two-sided answer:

> **Up to three sections you never needed, and up to three you would have failed without.** One line each,
> naming the section.

Both halves, or neither. A list of what to cut with nothing to keep is an opinion; the two together are a
measurement. If nothing stood out either way, say that too — `--ask none` is a real answer and more useful than
an invented one.

**Write it while the finding is fresh**, not in a batch at the end — an hour later it has lost the detail that
made it useful.

**Log the frictions, not only the failures.** Anything that took longer to work out than it should have is the
point of this run: a command whose error named the wrong cause, a document that sent you the wrong way, a step
you only got right on the fourth try. Those are what get fixed before the next person arrives — in this seed, or
in the tooling itself.

It is not homework. It is the deliverable that improves this for the next person, and the most useful thing you
will have when someone asks what the build actually cost.
