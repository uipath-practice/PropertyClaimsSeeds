# How to work in this folder

This is the seed for the Property Claims exercise. It describes what to build; you write everything that does the building.

**Read `README.md` for the steps and `PDD.md` for the process.** Neither is repeated here — this file is only about how to work.

## Where your work goes

| What you produce | Where |
|---|---|
| Generated code: Maestro Case and Agents | `Build/ClaimCase-<seat>/`, **one solution** |
| Coded Action App (validation) | `Build/claim-review-<seat>/`; **own publish and deploy** (`CONFIG.md`, *Deploying*). A Coded Process App (dashboard) is a later block, not in this seed |
| Documents you write for a block (design, task list, notes) | the block's own folder |
| Findings | the shared table, via `log-finding.py`. Never a local file |
| Where the build has got to, what exists, what broke, what is next | `PROGRESS.md`, at the root of this folder. The one file that spans blocks |

**Paths in this seed are relative to this folder**, always — `contracts/claim-entity.md`, never `../contracts/`. A block citing a path outside itself is telling you the knowledge is shared.

**Seed filenames are fixed**, so nothing you write can collide: a block ships `prompt.md` and `cookbook.md`, sometimes a script. **Any other file in a block folder is yours.**

**A file that configures the platform rather than shipping inside the solution belongs in its block folder too**, not in `Build/`. A schema, a fixture, a test matrix: generated, machine-readable, and not part of the package. `ls Build/` should show your solution and apps source code and nothing else.

## You have standing approval to build, deploy and run

Orchestrator seat folder and seat is yours: your own folder, buckets, solution, claim record and copies of the documents. Nothing in it is shared, nothing is production, all of it is disposable. **Creating resources, publishing, deploying, uninstalling and starting real runs are authorised in advance**, as often as you need, as is deleting and recreating something you made.

Two things make that safe: the claims are synthetic and the claimants are not real, and **no letter is ever sent** — correspondence is written and logged by existing process, but never delivered.

**Pausing for approval is not required.** A block's value is in what a live run reveals, and a build that stops at the deploy gate has proven nothing. Work to the goal, then report.

**Your harness may not honour this, and that is worth settling before you need it.** The commands that recover a broken deployment — uninstalling/reinstalling a solution, deleting a process, cancelling a case instance — read as destructive out of context and are the ones a safety classifier is most likely to refuse. Refused mid-block, the build stops dead with the fix identified and unrunnable. Ask your operator to allow the whole loop (pack, publish, deploy, upload) before the first deploy, not only for the recovery verbs.

**Three things are still worth a pause**, all outside your seat: touching another seat's folder or solution, changing anything at tenant level, and deleting a shared resource. If something you are about to run names a resource without your seat name in it, stop and ask.

## Rules that hold everywhere

**Names come from the contracts. Do not invent them and do not improve them.** A better name breaks a binding three blocks later, at run time, silently. [`CONFIG.md`](CONFIG.md) and [`contracts/claim-entity.md`](contracts/claim-entity.md) have the rules.

**Verify, do not assume.** Nearly every *"not found"* here is a wrong folder, a wrong tenant, a wrong scope or a stale cache rather than an absent resource. Check [`known-issues/`](known-issues/) before believing an empty `list`, and `uip login status` before believing anything is missing.

**Every block folder has a `cookbook.md` — issue → fix, from people who have done it before. When something fails, read the block's cookbook before searching further.**

**Check the platform's own tooling before hand-rolling.** `uip --help` and the installed skills are ahead of any document, this one included. Where they disagree with a cookbook, the tool wins — **and that disagreement is worth logging.**

**Before the first block, be on the toolchain line `CONFIG.md`, *Toolchain*, names.** `uip --version` shows yours; if it differs, run the commands there. Skills follow the CLI's `major.minor` line, and this seed was tested on exactly that one — a different line means different skills and a seed written for another.

**Load the right skill for the block, and only that one.** Several have names close enough that an agent follows instructions for a different product:

| Block | Skill |
|---|---|
| Design · Plan | `uipath-planner` designs, then derives the tasks |
| Build: IXP Extraction · Data Fabric Entity · Agents · Case Plan · Run · Coded Action App | `uipath-ixp` · `uipath-platform` · `uipath-agents` · `uipath-maestro-case` · `uipath-solution` · `uipath-coded-apps` |
| Verify · Hand over | `uipath-platform`, `uipath-troubleshoot` · `uipath-solution`, and `uipath-planner` for the as-built `sdd.md` — the planner is the sole author of a case SDD (its Rule 13) |

Three near-misses that have each cost time: **`uipath-maestro-bpmn` is not the case skill** — a case compiles to a file whose name ends `.bpmn`, which is not the same thing and is not authored by hand. **`uipath-maestro-flow` is not used here at all.** **`uipath-test` drives Test Manager**, which is not what Verify does.

**Fix what earlier blocks got wrong.** Each block inherits work made with less information than you have now, and correcting it is part of your block rather than a detour from it. Fix it at the source, say so in your notes, and log it — a defect one block leaves for another is usually a gap in what the seed told that block. Where you cannot fix it here, **write down the specific change required anyway**: an unfixed defect that is named is a task, and one that is silent is a landmine. The bar is *wrong*, not *not how I would have written it*.

**Do not read the answer key.** One of the files in the `Claims` bucket states the problems planted and the outcome expected — an analysis that consults it is brilliant and worthless. It is the test oracle and it is yours in Verify only. [`contracts/provided-processes.md`](contracts/provided-processes.md), *Where the files live*, names it so you can avoid it.

## Push the solution to Studio Web at the end of every block

**`uip solution upload Build/ClaimCase-<seat> --force`.** Everything you build is local until you do, and a solution that has never been uploaded is invisible in Studio Web. **Do it at the end of every block, not once at the end.** Until `Build/ClaimCase-<seat>` exists there is nothing to upload — blocks 1 and 2 create nothing, and 3a creates nothing on the platform. It makes it possible to review the build shape and make inflight adjustments.

**`--force` is required after the first upload and it wipes Studio Web's version history** for that solution. That is the right trade here — your history is in git and in `PROGRESS.md`, and the cloud copy is a view rather than a source.

## Keep a running record of where the build is

**`PROGRESS.md`, at the root of this folder, and it is the one file here you should be generous with.** Everything else in this seed is kept short deliberately. It is written for the agent running the next block, which starts with an empty context, no memory of what you did, and no way to find out except by redoing it.

**A skeleton ships with the seed — one section per block and the numbers each block owes. Read it before you start; fill it as you go, not before you finish.** Your context will be compacted without warning, more than once on a long block, and nothing that exists only in your context survives it. `PROGRESS.md` is your memory, not your report: append after every deploy cycle, every fixed defect and every decision — a name, a key, what you tried, what happened. If you notice a compaction has happened, re-read `PROGRESS.md` from the current block heading before doing anything else. Append, never rewrite: a fact that turned out to be wrong is corrected by a new line saying so, because the next block needs to know it was once believed.

| Put in it | Why |
|---|---|
| **Every name, key, id, folder, version and connection** you created or found | no document that ships with this seed can know them, and each one costs a command to rediscover |
| **The command that produced each**, and its output | so the next block re-verifies in one line instead of researching |
| **What the next block will need** — read its `prompt.md` before you finish and stage it | the cheapest minute in the whole exercise |
| **What went wrong and how you fixed it**, including what you tried first | the wrong turn is often more useful than the fix, because it is what the next block is about to take |
| **What you would do differently, and what you would do next** | you have context nobody after you will have |
| **What you could not verify** | an open question inherited out loud beats a silent assumption |


### Three places a problem gets written

The same event legitimately appears in all three. They are written for different readers, at different distances, and they have different lifetimes.

| | Who reads it | Lifetime | Shape |
|---|---|---|---|
| `PROGRESS.md` | the next block of **this** build | dies with this build | as long as it needs to be, raw output and all |
| the **findings table** | the people who maintain this exercise | one round | one finding, one thing, dated |
| `cookbook.md` | **every future participant** | until the platform or UiPath skills changes | **not yours to write.** It is maintained with the seed |

So: hit a wall, and write it **everywhere it belongs** — in `PROGRESS.md` so the next block does not hit it, and as a finding so it can become a cookbook line for everyone who comes after. Neither one makes the other redundant.

## Log what you learn

Findings go to a shared table so they can be counted across everyone doing this exercise, and `log-finding.py` is the whole interface to it. There is no local findings file.

**Identify yourself at the start of your session** — several agents write to this table at the same time, and a row naming the wrong model silently merges two of them:

```bash
python3 log-finding.py --identify "<your agent>" "<your model>" --effort "<your effort tier>"
```

If it answers *identity already recorded*, it was set for you before the session started — leave it.

Include the effort tier if your runtime has one. The same model at two tiers is two different builders, and without that word every comparison between runs is confounded. **If you are not certain which model you are, ask** — `unknown` is more useful than a plausible wrong answer.

```bash
python3 log-finding.py --block 1-design --category friction \
  --summary "What happened, what you tried, what happened next."
```

`--block` is the folder name exactly as it is spelled on disk. `--category` is free text; reuse one you have used before inventing a neighbour.

Four optional fields turn a finding into a recommendation: **`--source`** where the answer actually came from (`seed` · `skill` · `cli-help` · `docs` · `model` · `trial-error`) · **`--ask`** what should change (`keep` · `cut` · `fix` · `add` · `move` · `none`) · **`--artifact`** which file and section · **`--evidence`** the exact error or command. **`--evidence` holds 200 characters** — one error string, not a command and its output. Put the explanation in `--summary`, which is roomy.

**Never paste a secret, and never paste a whole file.** This table is shared with everyone on this tenant.

**Log a finding the moment you have it — not at the end of the task, and never at the end of the block.** Your context will be compacted, more than once on a long block, and a finding you were holding to write up later does not survive it. 

**End every block with `python3 log-finding.py --retry`** and report the count it gives back — that number is a fact about the table rather than about a command, and if it is short of what you logged, say so. 

### A finding is not only a complaint

The table's job is to make the next version of this seed better, and better is as often **shorter**. Three of the most useful things you can report are not problems:

- **"This was already handled"** — you read a page here, then found a skill or `--help` said the same. Ours is a page we should delete, but only safely if we know what replaced it.
- **"This saved me"** — a warning you read, believed, and would otherwise have walked into. Almost nobody reports these, and they are what makes cutting safe. **A trap you never met is not proof the warning was unnecessary — it may be proof that it worked.**
- **"This was in the wrong place"** — build mechanics sitting in a business brief, or a design decision buried in a list of commands.
- **"I retried"** — the same command a second time with a different flag, or a second diagnosis after the first was wrong. Log it as the friction it is, with both attempts. From outside a retry is invisible; from inside it is this exercise's most common cost.
- **"I decided this myself"** — every question you would have asked a human and answered instead. `--category assumption`, one line: the question and your answer.
- **"Two sources disagreed"** — a skill against this seed, or two files here against each other — and which you followed. Every one of these is a defect we cannot see from outside, because your build resolved it silently.

**Suggest a rewording only when you can say what it cost you.** *"This would read better as X"* is an opinion. *"I read this, did X for forty minutes, and the right answer was Y"* is a defect with a fix attached.

### Before you finish a block

**The block record goes in `PROGRESS.md` — the narrative, for the next block. The numbers go in one finding, `--category block-summary`:** wall-clock, deploy cycles, claims run, retries, wrong first diagnoses, questions you answered alone, and the three most expensive minutes and what caused them. One finding per block, before `--retry`. Nobody reads your terminal; this table and `PROGRESS.md` are all that reaches us.

Re-read what you were handed and log the two-sided answer, one finding per file: **up to three sections you never needed, and up to three you would have failed without.** One line each, naming the section. Both halves or neither — a list of what to cut with nothing to keep is an opinion; the two together are a measurement.

### Before you finish the exercise

Once, at the end, when you have seen the whole set. Four questions, one finding each, `--category seed-review`:

1. **Which single change would have saved you the most time?** Name the file and section. One answer — forcing the ranking is the point.
2. **What did you have to work out that no document told you?**
3. **Where did two documents disagree, and which did you follow?** Every one of these is a defect we cannot see from outside, because your build resolved it silently.
4. **What did you build that you now know is wrong**, and did you go back and fix it?

Answer from what happened, not from what would sound useful. A blank answer is a real answer.
