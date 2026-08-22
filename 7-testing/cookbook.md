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

`download` writes the file **to stdout** with a wrapper around it, so parse from the first `{` rather than piping
straight into a JSON reader. Bucket commands take the bucket's **key (a GUID)**; passing its name returns
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

uip tasks assign <task-id> --user-id <user-id>     # uip tasks users <numeric-id> lists them
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
- **A task arrives `Unassigned`, and completing one that is not yours fails** with *"This action is no longer
  assigned to you"* — which reads as though someone else took it, or the case moved on. Assign it first.
- **Writing task data REPLACES the payload; it does not merge.** Send only the decision and the identifying
  fields are gone, so the completed task can never be re-opened and read. Re-send them every time.

The `--action` is the decision: the app declares its outcomes, and `continue` / `deny` are the two here.

## Wait for a claim without guessing

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

Read the job, not the case:

```bash
uip or jobs get <faulted-job-key>      # `Info` carries the real exception
```

Two shapes worth recognising:

- **`BlobFileInfo does not exist`** on a document retrieval means the identifier the case is looking the document
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
