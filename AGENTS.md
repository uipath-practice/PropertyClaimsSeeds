# How to work in this folder

This is the seed for the Property Claims exercise. It describes what to build; you write everything that does the building.

**Read `README.md` for the steps and `PDD.md` for the process.** Neither is repeated here — this file is only about how to work.

## Where your work goes

| What you produce | Where |
|---|---|
| generated code — the case, the analyses, the screen | `Build/ClaimCase-<seat>/`, **one solution** |
| documents you write for a block — a design, a task list, notes | the block's own folder |
| findings | the shared table, via `log-finding.py`. **Never a local file** |
| where the build has got to — what exists, what broke, what is next | `PROGRESS.md`, at the root of this folder. **The one file that spans blocks**, and the one to be generous with |

**Paths in this seed are relative to this folder**, always — `contracts/claim-entity.md`, never `../contracts/`. A block citing a path outside itself is telling you the knowledge is shared.

**Seed filenames are fixed**, so nothing you write can collide: a block ships `prompt.md` and `cookbook.md`, sometimes a script. **Any other file in a block folder is yours.** A missing `spec.md` is information, not an omission — it means the specification is shared and lives in `contracts/` or `method/`.

**A file that configures the platform rather than shipping inside the solution belongs in its block folder too**, not in `Build/`. A schema, a fixture, a test matrix: generated, machine-readable, and not part of the package. `ls Build/` should show your solution and nothing else.

## You have standing approval to build, deploy and run

This seat is yours — your own folder, solution, claim record and copies of the documents. Nothing in it is shared, nothing is production, all of it is disposable. **Creating resources, publishing, deploying, uninstalling and starting real runs are authorised in advance**, as often as you need, as is deleting and recreating something you made.

Two things make that safe: the claims are synthetic and the claimants are not real, and **no letter is ever sent** — correspondence is written and logged, never delivered.

**Pausing for approval is the wrong instinct here and it is expensive.** A block's value is in what a live run reveals, and a build that stops at the deploy gate has proven nothing. Work to the goal, then report.

**Your harness may not honour this, and that is worth settling before you need it.** The commands that recover a broken deployment — uninstalling a solution, deleting a process, cancelling a case instance — read as destructive out of context and are the ones a safety classifier is most likely to refuse. Refused mid-block, the build stops dead with the fix identified and unrunnable. Ask your operator to allow them **before** the first deploy.

**Three things are still worth a pause**, all outside your seat: touching another seat's folder or solution, changing anything at tenant level, and deleting a shared resource. If something you are about to run names a resource without your seat name in it, stop and ask.

## Rules that hold everywhere

**Names come from the contracts. Do not invent them and do not improve them.** A better name breaks a binding three blocks later, at run time, silently. [`contracts/claim-entity.md`](contracts/claim-entity.md) has the rule.

**Verify, do not assume.** Nearly every *"not found"* here is a wrong folder, a wrong tenant, a wrong scope or a stale cache rather than an absent resource. Check [`known-issues/`](known-issues/) before believing an empty `list`, and `uip login status` before believing anything is missing.

**Check the platform's own tooling before hand-rolling.** `uip --help` and the installed skills are ahead of any document, this one included. Where they disagree with a cookbook, the tool wins — **and that disagreement is worth logging.**

**Load the right skill for the block, and only that one.** Several have names close enough that an agent follows instructions for a different product:

| Block | Skill |
|---|---|
| Design · Plan | `uipath-maestro-case` · `uipath-planner` |
| Build — extraction · claim record · analyses · case · screen | `uipath-ixp` · `uipath-platform` · `uipath-agents` · `uipath-maestro-case` · `uipath-coded-apps` |
| Verify · Ship | `uipath-platform`, `uipath-troubleshoot` · `uipath-solution` |

Three near-misses that have each cost time: **`uipath-maestro-bpmn` is not the case skill** — a case compiles to a file whose name ends `.bpmn`, which is not the same thing and is not authored by hand. **`uipath-maestro-flow` is not used here at all.** **`uipath-test` drives Test Manager**, which is not what Verify does.

**Fix what earlier blocks got wrong.** Each block inherits work made with less information than you have now, and correcting it is part of your block rather than a detour from it. Fix it at the source, say so in your notes, and log it — a defect one block leaves for another is usually a gap in what the seed told that block. Where you cannot fix it here, **write down the specific change required anyway**: an unfixed defect that is named is a task, and one that is silent is a landmine. The bar is *wrong*, not *not how I would have written it*.

**Do not read the answer key.** One of the files in the `Claims` bucket states the problems planted and the outcome expected — an analysis that consults it is brilliant and worthless. It is the test oracle and it is yours in Verify only. [`contracts/provided-processes.md`](contracts/provided-processes.md), *Where the files live*, names it so you can avoid it.

## When a block goes wrong — checkpoints

`checkpoints/` holds a working version of a block's output. Restore one and carry on. Using one is a **deliberate choice, not a failure**: a half-finished component everything downstream depends on is worse than a borrowed working one.

Two things keep it honest. **Read the block's prompt anyway** — later blocks bind these things by name, and debugging a wiring problem in something you have never looked at is the most expensive hour available here. And **log it**: which checkpoint, when, and what had gone wrong. That is the clearest signal we get about where this is too hard.

## Push the solution to Studio Web at the end of every block

**`uip solution upload Build/ClaimCase-<seat> --force`.** Everything you build is local until you do, and a solution that has never been uploaded is invisible in Studio Web however correct it is — including the case plan, which is the one artifact anybody looking over your shoulder wants to see.

**Do it at the end of every block, not once at the end.** It costs a command, it is how a human watches the build take shape, and a solution uploaded only at the end is one where nothing could be reviewed while it still mattered.

**`--force` is required after the first upload and it wipes Studio Web's version history** for that solution. That is the right trade here — your history is in git and in `PROGRESS.md`, and the cloud copy is a view rather than a source.

**One rule that makes this safe: never edit in Studio Web.** The sync runs one way for you. Opening the designer is fine — reading, looking at the case diagram, showing someone. Editing there and then uploading again from local silently discards whichever side you did not keep.

## Keep a running record of where the build is

**`PROGRESS.md`, at the root of this folder, and it is the one file here you should be generous with.** Everything else in this seed is kept short deliberately. This one is not — it is written for the agent running the next block, which starts with an empty context, no memory of what you did, and no way to find out except by redoing it.

**Read it before you start. Add to it before you finish.** Append, never rewrite: a fact that turned out to be wrong is corrected by a new line saying so, because the next block needs to know it was once believed.

| Put in it | Why |
|---|---|
| **Every name, key, id, folder, version and connection** you created or found | these are yours alone — no document that ships with this seed can know them, and each one costs a command to rediscover |
| **The command that produced each**, and its **raw output** | so the next block re-verifies in one line instead of researching. Paste the real output; a summary of it is worth less than the thing |
| **What the next block will need** — read its `prompt.md` before you finish and stage it | the cheapest minute in the whole exercise |
| **What went wrong and how you fixed it**, including what you tried first | the wrong turn is often more useful than the fix, because it is what the next block is about to take |
| **What you would do differently, and what you would do next** | you have context nobody after you will have |
| **What you could not verify** | an open question inherited out loud beats a silent assumption |

Length is not a virtue here and neither is brevity — **write what a competent stranger would need to carry on without you.**

### Three places a problem gets written, and they are not copies

The same event legitimately appears in all three. They are written for different readers, at different distances, and they have different lifetimes.

| | Who reads it | Lifetime | Shape |
|---|---|---|---|
| `PROGRESS.md` | the next block of **this** build | dies with this build | as long as it needs to be, raw output and all |
| the **findings table** | the people who maintain this exercise | one round | one finding, one thing, dated |
| `cookbook.md` | **every future participant** | until the platform changes | a short hint — and **not yours to write.** It is distilled by the maintainers once the same thing has been seen on more than one build |

So: hit a wall, and write it **everywhere it belongs** — at length in `PROGRESS.md` so the next block does not hit it, and as a finding so it can become a cookbook line for everyone who comes after. Neither one makes the other redundant.

## Log what you learn

**One command, one sink.** Findings go to a shared table so they can be counted across everyone doing this exercise, and `log-finding.py` is the whole interface to it. There is no local findings file.

**Say who you are once, at the start of your session** — several agents write to this table at the same time, and a row naming the wrong model silently merges two of them:

```bash
python3 log-finding.py --identify "<your agent>" "<your model>" --effort "<your effort tier>"
```

Include the effort tier if your runtime has one. The same model at two tiers is two different builders, and without that word every comparison between runs is confounded. **If you are not certain which model you are, ask** — `unknown` is more useful than a plausible wrong answer.

```bash
python3 log-finding.py --block 1-design --category friction \
  --summary "What happened, what you tried, what happened next."
```

`--block` is the folder name exactly as it is spelled on disk. `--category` is free text; reuse one you have used before inventing a neighbour.

Four optional fields turn a finding into a recommendation: **`--source`** where the answer actually came from (`seed` · `skill` · `cli-help` · `docs` · `model` · `trial-error`) · **`--ask`** what should change (`keep` · `cut` · `fix` · `add` · `move` · `none`) · **`--artifact`** which file and section · **`--evidence`** the exact error or command. **`--evidence` holds 200 characters** — one error string, not a command and its output. Put the explanation in `--summary`, which is roomy.

**Never paste a secret, and never paste a whole file.** This table is shared with everyone on this tenant.

**Log a finding the moment you have it — not at the end of the task, and never at the end of the block.** Your context will be compacted, more than once on a long block, and a finding you were holding to write up later does not survive it. What survives is what you already sent. This is not tidiness: whole rounds have reached the end of a block with a working build and almost nothing to show for how it was reached, which is the half of the exercise we cannot reconstruct afterwards. **If you notice it, send it, then carry on** — it costs one command.

**End every block with `python3 log-finding.py --retry`** and report the count it gives back — that number is a fact about the table rather than about a command, and if it is short of what you logged, say so. Telemetry that fails quietly is worth more to us than the findings it swallowed.

### A finding is not only a complaint

The table's job is to make the next version of this seed better, and better is as often **shorter**. Three of the most useful things you can report are not problems:

- **"This was already handled"** — you read a page here, then found a skill or `--help` said the same. Ours is a page we should delete, but only safely if we know what replaced it.
- **"This saved me"** — a warning you read, believed, and would otherwise have walked into. Almost nobody reports these, and they are what makes cutting safe. **A trap you never met is not proof the warning was unnecessary — it may be proof that it worked.**
- **"This was in the wrong place"** — build mechanics sitting in a business brief, or a design decision buried in a list of commands.

**Suggest a rewording only when you can say what it cost you.** *"This would read better as X"* is an opinion. *"I read this, did X for forty minutes, and the right answer was Y"* is a defect with a fix attached.

### Before you finish a block

Re-read what you were handed and log the two-sided answer, one finding per file: **up to three sections you never needed, and up to three you would have failed without.** One line each, naming the section. Both halves or neither — a list of what to cut with nothing to keep is an opinion; the two together are a measurement.

### Before you finish the exercise

Once, at the end, when you have seen the whole set. Four questions, one finding each, `--category seed-review`:

1. **Which single change would have saved you the most time?** Name the file and section. One answer — forcing the ranking is the point.
2. **What did you have to work out that no document told you?**
3. **Where did two documents disagree, and which did you follow?** Every one of these is a defect we cannot see from outside, because your build resolved it silently.
4. **What did you build that you now know is wrong**, and did you go back and fix it?

Answer from what happened, not from what would sound useful. A blank answer is a real answer.
