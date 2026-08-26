# The provided automations

Six automations are deployed in your folder before you start. **You bind them; you never open or rebuild them.** They are the integration layer — in a real insurer these drive an insurer portal to fetch a policy, search, download a PDF and hand it back. Here that is a storage bucket behind the same interface, which keeps the shape while removing a dependency nobody can provision for a room full of people.

Which `PDD.md` business system each one stands for is in [`CONFIG.md`](../CONFIG.md), *What already exists*.

## Read the arguments from the platform, not from here

**This file explains what each one is for. The platform is authoritative on its arguments.**

```bash
uip or processes list --folder-key <your seat folder> --output json   # what is deployed, and its version
uip or packages entry-points "<PackageId>:<Version>" --output json    # its exact I/O schema
```

**Read the version out of the process list first.** `entry-points` at a version that does not exist answers `Result: Success` with an empty `Data` array — which reads as *this process declares no arguments* rather than *no such version*. Not all six are on `1.0.0`.

**Expect more than one entry point.** `Retrieve Property Claim` has two, with different required arguments: one requires all of `in_Scenario`, `in_Discrepancy`, `in_ClaimID` and returns nothing; the other requires none and returns `out_ClaimID`. **Always supply all three**, empty strings where you are not aiming the run — valid against either, where supplying only `in_ClaimID` faults one of them with `170002`.

`uip maestro case tasks describe --type process` looks like the right command and is not — it accepts `process` and reports no entry found.

**If this file and `entry-points` disagree, the platform wins, and the disagreement is worth logging.**

## The six

| Automation | Serves | Give it | Get back |
|---|---|---|---|
| `Retrieve Property Claim` | steps 1.1, 1.2 | a claim number, optionally an aimed scenario | the three documents land in the buckets; echoes `out_ClaimID` |
| `Extract Claim Data (IXP)` | step 1.3 | the claim number | the claim as structured data, the policy number, and the form as a file |
| `Retrieve Policy Document` | step 1.4 | a policy number | the policy document |
| `Retrieve Previous Claims` | step 1.5 | a policy number | what has been claimed against that policy before |
| `Retrieve Inspection Report` | step 3.1 | the claim number | a ready flag, and the report once it exists |
| `Client Notification` | steps 1.6, 6.3, 7.2 | subject, body, recipient | nothing |

### Three shapes that are easy to get wrong

A mismatch here faults at run time having packed and deployed cleanly.

- **The extracted claim is an object, not a string.** An input declared `type: object` takes it directly.
- **The claim history is a string**, not an object — the opposite, in the same plan.
- **The three document outputs are job attachments.** Bind one to an attachment-typed input, never to a string.

## What each one does

**`Retrieve Property Claim`** generates a claim and uploads all three documents. `in_ClaimID` is the number stamped on them — pass your case's own external id so the case and the documents agree. `in_Scenario` and `in_Discrepancy` aim the run at a known problem; leave them empty for a random claim. Safe to call once per claim, and **it should not run again if a stage re-enters** — regenerating a claimant's documents mid-case is not a thing that happens in reality.

Its `out_ClaimID` is the file it wrote, which is the number you passed in. **You almost certainly should not bind it** — binding it to your own claim identifier gives that value two sources, and the one you did not intend wins whenever they differ.

**`Extract Claim Data (IXP)`** reads the claim form and runs the extraction model over it. **Only the claim form is extracted** — the policy and the assessor's report are prose and are read as documents (`PDD.md` §5.6).

**The extracted payload is deeply nested, and a case expression resolves one level.** Every group is an array and every field is an object:

```
ClaimClaimant[0].EmailAddress.Value            group → array, field → { Value, Confidence, OcrConfidence }
ClaimGeneral[0].TotalClaimed.Value.Value       money nests once more: .Value.Value and .Value.Currency
```

So **anything the case itself has to read — above all the claimant's contact details for step 1.6 — has to be surfaced as a plain scalar by whatever step produces it.** A binding that reaches into the raw payload fails on every claim, loudly, on a required argument. Which step surfaces it is your design decision; that it must be surfaced is not.

**`Retrieve Policy Document`** fetches the policy by number, so it cannot run before extraction — the number comes from the claim form. That single dependency is most of why Intake has the shape it does.

**`Retrieve Previous Claims`** returns the claim history for a policy, as a JSON string. **An empty history is a result, not a failure** (`PDD.md` step 1.5).

**`Retrieve Inspection Report`** fetches the assessor's report. **It does not fail when the report is not there yet** — it returns `out_ReportReady: false` and no file, which is what makes a waiting stage possible: call it, test the flag, move on or wait and call again. Treat anything other than an explicit `true` as not-ready.

**How long "not yet" lasts is decided by your poll interval, not by the assessor.** The stand-in models no timer: **every call is an independent draw, ready about four times in five.** Expected wait is roughly one and a quarter calls, and the wall clock is whatever you multiply that by. There is nothing to wait *for* — pick a short interval.

**`Client Notification`** takes a subject, a body and a recipient and **writes them to the job log. It does not send email**, and no email connection is provisioned. Bind the letter you would have sent; it is then visible in the log and recorded on the claim. Its recipient argument is spelled **`in_Recepient`** — a typo in the process, not in this document. Bind the spelling the platform reports.

## Where the files live

Three buckets, in your folder.

| Bucket | Holds |
|---|---|
| `Claims` | `<claimId>-claim.pdf`, the answer key as `<claimId>-claim.json`, and the policy's history as `<policyId>-history.json` |
| `Insurance Policies Repository` | `<policyId>.pdf` |
| `Assessor Reports` | `<claimId>-incident-report.pdf` |

The claim history is keyed by **policy**, not by claim, and lives in the `Claims` bucket beside the claim forms.

**`<claimId>-claim.json` is the answer key and nothing you build may read it.** It states which problems were planted and what the outcome should be — the test oracle, and yours in the Verify block only. It is named after the claim PDF rather than `manifest.json`, so looking for that name in the bucket finds nothing.

## The one thing that will bite you

**These live in your seat folder, not in your solution's folder.** Deploying creates a sub-folder, and a sub-folder does not inherit its parent's processes, so **every binding needs its folder named explicitly** — `ClaimCase-<seat>`.

Get it wrong and the case faults about five seconds in with *"the job's associated process could not be found"*, having executed nothing. The message names the process; the problem is the folder it was looked for in.
