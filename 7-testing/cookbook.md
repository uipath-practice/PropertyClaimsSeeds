# Running the tests — the commands, and where they mislead

Companion to `7-testing/spec.md`, which says *what* to assert. This says how to get the numbers out, and
which of these commands lie to you.

Everything here was run against a live tenant. Where a command has a trap, the **symptom** is given rather than
the fix, because the symptom is what you will actually meet.

## Skill, and how many runs

**Skill.** `uipath-platform` to start runs and read state; `uipath-troubleshoot` when one fails and you need to
know why. **Not `uipath-test`** — that drives Test Manager, which this exercise does not use.

**Running claims is pre-authorised** (`AGENTS.md`) — do not stop to ask before a run.

Thirty-one runs, in this order, and the order matters: **nine pinned, then two clean, then twenty unaimed.**
Pinned first because a failure there names its own cause; unaimed last because a random claim that misbehaves is
only diagnosable once you know the nine work. Do not start the twenty while the nine are failing.

## Aim a claim

The case takes two input arguments, so a run is aimed without touching the case plan:

```bash
uip or jobs start <case-process-key> --folder-key <solution-folder-key> \
  --input-arguments '{"scenario":"eligibility-fail","discrepancy":"ELIG_ADDRESS_MISMATCH"}'
```

**Confirm the arguments actually arrived somewhere.** They travel case argument → case variable → the document
generator's own inputs, and a break anywhere in that chain is silent — the claim generates fine, just not the one
you asked for. The generator runs as a child job in the **parent** folder, and its job record shows what it
received:

```bash
uip or jobs list --folder-key <parent-folder-key> --limit 20      # newest first
uip or jobs get <child-job-key>                                   # InputArguments / OutputArguments
```

A correct chain looks like this — note the names change on the way through, which is normal:

```
case job       In: {"scenario":"eligibility-fail","discrepancy":"ELIG_ADDRESS_MISMATCH"}
generator job  In: {"in_Scenario":"eligibility-fail","in_Discrepancy":"ELIG_ADDRESS_MISMATCH",
                    "in_ClaimID":"CLM-HO-73713221"}
```

> **`--input-arguments` is accepted whether or not anything reads it.** `jobs start` returns Success for a case
> that declares no arguments at all. The child job's `InputArguments` is the only proof.

## Read the answer key

The manifest sits beside the claim in the claims bucket, named after the claim:

```bash
uip or bucket-files list <bucket-key> --folder-key <parent-folder-key>
uip or bucket-files download <bucket-key> "/<claimId>-claim.json" --folder-key <parent-folder-key>
```

**Answer keys accumulate, and old ones do not expire.** The bucket holds every claim your seat has ever
generated, including ones written by an earlier generator version whose expectations differ from the current
rules. Read the key for **the claim you just ran**, by its own id — never "the newest `*-claim.json`", and never
a key you cached in an earlier block. A stale key scores a correct build as broken and the disagreement looks
like your solution.

`download` writes the file **to stdout** with a wrapper around it, so parse from the first `{` rather than piping
straight into a JSON reader.

**And it fails intermittently while looking exactly like success**: exit code `0`, and an error *document* on
stdout that your "parse from the first `{`" recipe parses perfectly —

```json
{"Result":"Failure","Message":"Error downloading file from bucket","Instructions":"fetch failed"}
```

A harness that caches that has just written an answer key with **no `AppliedDiscrepancies` in it**, so every
later assertion reads the claim as clean and an *aimed* claim scores as a clean-claim pass. Green, and
completely wrong. **Keep the payload only if it carries `ClaimId`, and retry if it does not** — the same
download succeeds on the next attempt. Bucket commands take the bucket's **key (a GUID)**; passing its name returns
*"Invalid bucket key: 'Claims'. Expected a UUID"*, which reads like the bucket is missing.

## Read what the analyses reported

The claim record holds every analysis payload. Two things about reading it:

```bash
uip df entities list                       # find the entity's id
uip df records get <entity-id> <record-id>
```

- **`records get` wants the entity's id, not its name.** With the name it returns *"The value 'ClaimCase' is not
  valid"* — which sounds like the entity does not exist, and it does.
- **Field names come back PascalCase**, whatever the entity declares. `eligibilityChecksJson` is read back as
  `EligibilityChecksJson`. Reading the camelCase name returns `None` for every field, and a validation script
  written that way reports that **every analysis missed everything** — a very convincing wrong answer. Accept
  both spellings.

## Drive a human gateway

Three commands, and the first is the one nobody expects to need.

```bash
uip or folders get <folder-key>                    # the *numeric* Id, which tasks commands want
uip tasks list --folder-id <numeric-id>
uip tasks get <task-id>                            # claim id, record id, which gateway

uip tasks assign <task-id> --user-id <user-id>     # ONLY if the task arrived unassigned — see below
uip tasks complete <task-id> --folder-id <numeric-id> \
  --type AppTask --action continue \
  --data '{"recordId":"…","claimId":"…","triggerStage":"eligibility",
           "decision":"continue","reviewerNotes":"…","reviewedAt":"2026-08-13T10:45:00Z"}'
```

Four traps in that block, in the order you will hit them:

- **The task commands are `uip tasks`, not `uip or tasks`.** The latter is not a command; a polling loop built on
  it reports zero tasks forever, which looks exactly like a case that never reached its gateway.
- **They take `--folder-id`, a number, while everything else takes `--folder-key`, a GUID.** `uip or folders get`
  is where the number comes from.
- **Assignment is conditional, not a step.** If your case sets `data.recipient` on the action task, every task
  arrives already assigned to you and `tasks assign` is never needed — one build ran the whole block without it.
  If it does not, the task arrives `Unassigned` and completing one that is not yours fails with *"This action is
  no longer assigned to you"*, which reads as though someone else took it or the case moved on. Check first,
  assign only if you must.
- **Writing task data REPLACES the payload; it does not merge.** Send only the decision and the identifying
  fields are gone, so the completed task can never be re-opened and read. Re-send them every time.

The `--action` is the decision: the app declares its outcomes, and `continue` / `deny` are the two here.

## Wait for a claim without guessing

**Identify a run by its case instance, not by hunting the generator's job.** The case job key **is** the maestro
instance id, and one call gives you the claim id:

```bash
uip maestro case instance get <case-job-key> --folder-key <solution-folder-key>   # ExternalId == the claimId
```

Scanning `or jobs list` for the generator's child job — the obvious approach — worked at a two-minute inspection
poll and **breaks at the ten-second poll this seed tells you to set**: every in-flight claim fires a poll job
every ten seconds, so the generator's row is pages deep within a minute, and identifying each row costs its own
`jobs get` because `jobs list` does not return `ReleaseName`. Measured: scanning 200 rows took five minutes and
found none of ten in-flight claims. The aim is confirmed by the manifest anyway, which the generator wrote from
the arguments it actually received.

A claim takes minutes and spends most of them idle. Count what is still moving rather than sleeping a fixed time:

```bash
uip or jobs list --folder-key <solution-folder-key> --limit 200 \
  | python3 -c "import json,sys,collections; r=json.load(sys.stdin)['Data']; \
                print(len(r), collections.Counter(x['State'] for x in r))"
```

**Raise the limit and treat the count as part of the answer.** The default returns 50 rows newest-first, and a
case job starts *before* every child it spawns — so its own children push it off the first page. A listing that
returns exactly the limit is truncated and means nothing.

## When a claim faults

**If a *job* faulted, read the job. If the *claim* faulted with no failed job, read the case** — the fault is in
the case engine and `jobs get` will tell you nothing:

```bash
uip or jobs get <faulted-job-key>      # `Info` carries the real exception
uip maestro case instance incidents <instance-id> --folder-key <solution-folder-key>
```

**Read the incident from the end.** `ErrorDetails` begins with the **entire compiled rules document** — 27,000
characters of it — and the actual message is the last line after the closing brace
(`Error: Cannot read property 'verdict' of null`). Piped through `head`, or skimmed in a terminal, it looks like
a dump of your own case plan with no error in it.

And the `ElementId` on the incident **can name an element that is nowhere in `caseplan.json`** — a synthetic one
such as `CaseRulesEvaluatorNode`. Grepping your plan for it finds nothing and reads like a corrupted deployment;
it is not, it is the rules evaluator, and it means every condition was evaluated at case start
(`5-case/spec.md`).

Two shapes worth recognising:

- **`BlobFileInfo does not exist`** *(rare — one build met it never in 60 runs)* on a document retrieval means the identifier the case is looking the document
  up by does not match the file that was written. Extraction confidence is the usual cause — a digit dropped from
  a policy number is enough — and it is worth logging rather than retrying blindly.
- **A downstream analysis failing schema validation on a file input** (`…PDF.ID Field required`) is almost always
  a *consequence*: something earlier failed to fetch the document, so the input is empty rather than malformed.
  Fix the first fault and the second disappears.

## Keep a log

As you test, log findings with `log-finding.py`. Add one whenever you retry something, get a
result you did not expect, or have to work out something these instructions did not explain — what you tried,
what happened, what you did next. Do not tidy it up afterwards and do not omit the dead ends; the dead ends are
the point.
