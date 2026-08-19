# Block 5 — getting the case plan built and deployed

The spec is `5-case/spec.md`. This is the platform friction, and there is more of it here than in any other
block. Read the first section before you edit anything: it is the one that costs a day if you meet it cold.

## `caseplan.json` is not what runs

The file you edit is source. The runtime executes **`caseplan.json.bpmn`**, a compiled artifact sitting beside it.

- `pack` **copies** the compiled file. It does not build it.
- No CLI command reliably regenerates it.
- **Opening the project in Studio Web is what recompiles it.**

So a hand edit to `caseplan.json` can pack, deploy and run while changing nothing at all, and every symptom points
somewhere else. Before believing any edit took effect:

```bash
grep -c "<a-token-that-exists-nowhere-else>" caseplan.json.bpmn
```

Pick a string your edit introduces that appears nowhere else — a new task name, a new variable. If the count is
zero, the runtime has not seen your change, whatever the deploy said.

## `uip maestro case validate` may or may not work — check, then pin

It has rejected plans outright with `[version] Invalid input: expected "27.0.0"` while the designer writes
`30.0.0`, and it has also run clean and caught real bugs. **Which you get depends on your CLI version**, and the
CLI moves on its own — it has been observed replacing 1.200.0-preview.117 with 1.199.0-preview.116 mid-session
and calling it an update.

So: try it. If it validates, use it — it catches things the script below cannot, like duplicate task names. If
it refuses on the version, do not downgrade your plan to satisfy it; that is a schema the designer will
overwrite. Either way **record `uip --version` in `build-findings.md`**, because this is the class of result that
is undiagnosable afterwards.

**The gate that always works is the script shipped beside this file:**

```bash
python3 5-case/check_caseplan.py caseplan.json
```

It runs in about a second, needs no tenant, and catches the three classes that fail silently at run time: a
`vars.X` nothing declares, an id pointing at something that no longer exists, and a stage entering on
`exited(...)` from a stage that marks itself complete. Run it after **every** edit, before every pack.

One failure is worth knowing by name: **a stage with no `layout.nodes` entry crashes the Studio Web designer on
load**, with an error naming nothing in your plan (`Cannot read properties of undefined (reading 'x')`). If the
canvas dies after you added a stage, that is why.

## Local files and Studio Web — never let them drift

The sync is automatic in **one direction only**: opening the project in Studio Web writes the tenant's state
*down* over your local folder, wholesale. Nothing ever pushes local work up for you. So there is exactly one way
to lose work — open Studio Web while local is ahead.

The loop that is safe:

1. Edit locally.
2. `python3 5-case/check_caseplan.py caseplan.json`
3. Upload your work **before** opening the designer.
4. Open the project in Studio Web once — this is what recompiles the `.bpmn`.
5. `grep -c` your token in the `.bpmn` to prove the recompile happened.

**Studio Web saves the plan minified onto a single line.** A 100 KB single-line JSON file is unreadable by tools
that slice by line, so pretty-print it after every round trip. Formatting is inert — it changes nothing the
runtime sees.

## Deploying, and the traps in order

**Uninstall before you pack.** Packing while a deployment is live mints duplicate resources named `..._1` — one
per agent and process the deployment owns — *during* the pack, after any cleanup you ran. Measured both ways: 8
duplicates with the deployment live, zero with it uninstalled, same folder, same files.

The order that works is **uninstall → clean → pack → deploy**.

Cleaning means deleting the numbered files, and the suffix **increments every cycle** (`_1`, then `_2`), so a
`*_1` filter silently stops matching on the second pass:

```bash
find resources -type f -name "*_[0-9].json" -delete
find resources -type f | wc -l          # know your clean baseline and check it
```

**Uninstall refuses while any job is non-final — and it is the *job* that blocks, not the case instance.** An
instance can read `Completed` while its job is still `Running`. Stop the job, and cancel any non-final instance;
a faulted agent leaves a case `Running (With Faults)` forever.

**Raise the list limit or you will not see the blocking job.** `jobs list` returns 50 rows newest-first, and the
parent case job starts *before* every task job it spawns — so its own children push it off the first page. If the
row count equals the limit, the answer is truncated and means nothing.

```bash
uip or jobs list --folder-key <f> --limit 200 --output json \
  | python3 -c "import json,sys,collections; r=json.load(sys.stdin)['Data']; \
                print(len(r), collections.Counter(x['State'] for x in r))"
```

**`Reason: Unauthorized` means "not found".** It appears when a solution pins a package version that is not in the
feed. Nothing is wrong with your permissions and re-authenticating is wasted effort — check the version.

## When a claim does not do what you expected

Two commands answer most of it, and the second settles arguments:

```bash
uip maestro case instance incidents <id> -f <folder>   # the error code and message
uip maestro case instance asset <id> -f <folder>       # the DEPLOYED plan, bindings resolved
```

`asset` returns what is actually running rather than what is in your folder. Most of this block's mysteries are a
difference between those two, so reach for it early.

Reading execution history, expect generated elements you did not author — re-entry counters, variable resets,
parallel gateway markers, per-stage completion trackers. Your own task ids appear verbatim alongside them.

## What a green run does not prove

A case can reach an ending with a stage that never started. Check the stages, not just the outcome: every stage
the claim entered should show complete, and the claim record should carry columns written by each of them. A gap
in the record is a stage that was skipped, and it is invisible anywhere else.
