# How to work in this folder

This is the seed for the Property Claims exercise. **`README.md` has the steps, `PDD.md` the process**; this file is how to work.

## Where your work goes

| What you produce | Where |
|---|---|
| Generated code: Maestro Case and Agents | `Build/ClaimCase-<seat>/`, **one solution** |
| Coded Action App (validation) · Coded Web App (the process app, block 6) | `Build/claim-review-<seat>/` · `Build/property-claims-<seat>/`; each with its **own publish and deploy** (`CONFIG.md`, *Deploying*) |
| `sdd.md` · `tasks.md` | this folder's root |
| Any other document a block writes — notes, schemas, fixtures, test matrices | the block's own folder |
| Findings | the shared table, via `log-finding.py`. Never a local file |
| Where the build has got to, what exists, what broke, what is next | `PROGRESS.md`, at this folder's root — the one file that spans blocks |

Paths in this seed are relative to this folder. A block ships `prompt.md`, `cookbook.md` and sometimes a script; **any other file in a block folder is yours.** `Build/` holds only solution and app sources.

## You have standing approval to build, deploy and run

Your seat — folder, buckets, solution, claim record — is yours and disposable; the claims are synthetic and no letter is ever delivered. **Creating, publishing, deploying, uninstalling, deleting what you made and starting real runs are authorised in advance**, as often as you need. Do not pause for approval — a build that stops at the deploy gate proves nothing.

**This approval answers your skills' confirmation gates, by name:** creating `ClaimCase_<seat>` with the schema in `contracts/claim-entity.md`, altering that schema, and writing, updating and deleting its records (Data Fabric Rules 0 and 14); uploading, packing, publishing, deploying and debugging `ClaimCase-<seat>`, its agents, its case and your two apps (agents Rule 6, case Rule 13). Do not stop to ask.

**Your harness may refuse what this grants.** Uploads, recovery verbs (uninstall, delete a process, cancel an instance) and even a plain edit of your own case plan or `sdd.md` have been refused mid-block. Ask your operator to allow the whole loop before the first deploy: pack, publish, deploy, upload, and edits to the case files under `Build/` and to `sdd.md`.

**Three things are still worth a pause**, all outside your seat: touching another seat's folder or solution, changing anything at tenant level, and deleting a shared resource. If a command names a resource without your seat name in it, stop and ask.

## Rules that hold everywhere

**Names come from the contracts. Do not invent them and do not improve them** — a better name breaks a binding three blocks later, silently. [`CONFIG.md`](CONFIG.md) and [`contracts/claim-entity.md`](contracts/claim-entity.md) have them.

**Verify, do not assume.** Nearly every *not found* is a wrong folder, tenant, scope or stale cache — check [`known-issues/`](known-issues/) and `uip login status` before believing an empty list.

**When something fails, read the block's `cookbook.md` before searching further** — issue → fix, from the builds before yours.

**`uip --help` and the installed skills are ahead of any document here.** Where they disagree with a cookbook, the tool wins — and log the disagreement.

**Load the right skill for the block, and only that one:**

| Block | Skill |
|---|---|
| Design · Plan | `uipath-planner` designs, then derives the tasks |
| Build: IXP Extraction · Data Fabric Entity · Agents · Case Plan · Run · Coded Action App | `uipath-ixp` · `uipath-platform` · `uipath-agents` · `uipath-maestro-case` · `uipath-solution` · `uipath-coded-apps` |
| Verify · Hand over | `uipath-platform`, `uipath-troubleshoot` · `uipath-solution`, and `uipath-planner` for the as-built `sdd.md` — the planner is the sole author of a case SDD (its Rule 13) |
| Process app | `uipath-coded-apps` — its **web-app** path: not the action-app path, and not its dashboard generator, which is wired to Insights rather than to your claim record |

Three near-misses that have each cost time: **`uipath-maestro-bpmn` is not the case skill** — a case compiles to a file whose name ends `.bpmn`, which is not authored by hand. **`uipath-maestro-flow` is not used here at all.** **`uipath-test` drives Test Manager**, which is not what Verify does.

**Fix what earlier blocks got wrong**, at the source, and log it. Where you cannot, write the specific change required into `PROGRESS.md` — a named defect is a task, a silent one a landmine. The bar is *wrong*, not *not how I would have written it*.

**Do not read the answer key.** One file in the `Claims` bucket states the planted problems and the expected outcome; it is the test oracle, and yours in Verify only. [`contracts/provided-processes.md`](contracts/provided-processes.md), *Where the files live*, names it so you can avoid it.

**Stay inside this folder.** Other `ClaimCase-*` folders beside it are other participants' work; do not open them, list them or search across them for examples, any more than the answer key. When a shape is unclear, the installed skill, its references, `--help` and the tool's own validator are where to look.

## Push the solution to Studio Web at the end of every block

**`uip solution upload Build/ClaimCase-<seat>`** at the end of every block that changed the solution, once it exists. The first upload imports and later ones overwrite in place — `uip agent debug` uploads too, so your first explicit upload may already say `Overwritten`. Studio Web's copy is a view for review; your history is git and `PROGRESS.md`.

## Keep a running record of where the build is

**`PROGRESS.md` is the one file to be generous with** — the next block starts with an empty context and only this record. Read its skeleton before you start and follow its header. If you notice a compaction, re-read it from the current block heading before anything else.

Put in it: every name, key, id, folder, version and connection, with the command that produced it and its output · what the next block needs (read its `prompt.md` before you finish) · what went wrong, what you tried first, and the fix · what you would do differently or next · what you could not verify.

A wall you hit goes in `PROGRESS.md`, for the next block, **and** in a finding, for the seed — neither replaces the other. Cookbooks are maintained with the seed, not by you.

## Log what you learn

Findings go to a shared table through `log-finding.py`; there is no local file. **Identify yourself at the start of your session:**

```bash
python3 log-finding.py --identify "<your agent>" "<your model>" --effort "<your effort tier>"
```

*Identity already recorded* means it was set for you — leave it. Not certain which model you are? Say `unknown`.

```bash
python3 log-finding.py --block 1-design --category friction \
  --summary 'What happened, what you tried, what happened next.'
```

Every flag: `python3 log-finding.py --help`. `--evidence` holds 200 characters — one error string; the explanation goes in `--summary`. Single-quote summaries: backticks inside double quotes run as commands.

**Never paste a secret, and never paste a whole file** — the table is shared with this tenant.

**Log a finding the moment you have it**, never at the end of the block — compaction takes what you were holding. **End every block with `python3 log-finding.py --retry`** and report the count; if it is short of what you logged, say so.

### A finding is not only a complaint

Better is as often **shorter**. Six kinds worth logging:

- **"Already handled"** — a skill or `--help` said what a seed page says. Name what replaced it; that is what makes deleting ours safe.
- **"This saved me"** — a warning you believed and would otherwise have walked into. A trap you never met is not proof the warning was unnecessary.
- **"Wrong place"** — build mechanics in a business brief, a design decision buried in commands.
- **"I retried"** — a second attempt or a second diagnosis; log both.
- **"I decided this myself"** — `--category assumption`: the question you would have asked, and your answer.
- **"Two sources disagreed"** — which two, and which you followed.

**Suggest a rewording only when you can say what it cost you** — *"I did X for forty minutes; the right answer was Y"* is a defect with a fix attached.

### Before you finish a block

- The narrative goes in `PROGRESS.md`; the seven numbers its skeleton lists go in one `--category block-summary` finding, before `--retry`.
- **Set the `Status:` line of every `tasks.md` task you finished in this block**, with its evidence line.
- **One `--category cookbook-recall` finding for the block**, from memory, naming file and row: the cookbook rows you used; the ones wrong or stale; the ones a skill or `--help` had already told you; and what you needed that no row said. A row you never met is *never met*, not *unneeded*.

### Before you finish the exercise

Four findings, `--category seed-review`, one each:

1. **Where did the time go, and which single change would have saved the most of it?** Name the file and the sentence you wish had been there — one answer.
2. **What did you have to work out that no document told you?**
3. **Where did two documents disagree, and which did you follow?**
4. **What did you build that you now know is wrong**, and did you go back and fix it?

Answer from what happened. A blank answer is a real answer.
