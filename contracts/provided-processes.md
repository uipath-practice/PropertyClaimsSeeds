# The provided automations

Six automations are deployed in your folder before you start. **You bind them; you never open or rebuild them.** They are the integration layer — in a real insurer these drive an insurer portal to fetch a policy, search, download a PDF and hand it back. Here that is a storage bucket behind the same interface, which keeps the shape while removing a dependency nobody can provision for a room full of people.

Which `PDD.md` business system each one stands for is in [`CONFIG.md`](../CONFIG.md), *What already exists*.

## Read the arguments from the platform, not from here

**This file explains what each one is for. The platform is authoritative on its arguments.**

```bash
uip or processes list --folder-key <your seat folder> --output json   # what is deployed, and its version
uip or packages entry-points "<PackageId>:<Version>" --output json    # its exact I/O schema
```

**Read the version out of the process list first** — not all six are on `1.0.0`, and `entry-points` at a wrong version does not tell you so (`known-issues/cli-commands.md`).

**Expect more than one entry point.** `Retrieve Property Claim` has two, with different required arguments: one requires all five — `in_Scenario`, `in_Discrepancy`, `in_ClaimID`, `in_ProfileId`, `in_Seed` — and returns nothing; the other requires none and returns `out_ClaimID`. **Always supply all five**, empty strings (and `0` for `in_Seed`) where you are not aiming the run — valid against either, where supplying only `in_ClaimID` faults one of them with `170002`.

**If this file and `entry-points` disagree, the platform wins, and the disagreement is worth logging.**

## The six

**In the case, each is an `rpa` task** — not `process`, which on this tenant resolves against an empty registry (`3d-case/cookbook.md`); the planner types them `process` and the design has to be corrected.

| Automation | Serves | Give it | Get back |
|---|---|---|---|
| `Retrieve Property Claim` | steps 1.1, 1.2 | a claim number, optionally an aimed scenario | the three documents land in the buckets; echoes `out_ClaimID` |
| `Extract Claim Data (IXP)` | step 1.3 | the claim number | the claim as structured data, the policy number, and the form as a file |
| `Retrieve Policy Document` | step 1.4 | a policy number | the policy document |
| `Retrieve Previous Claims` | step 1.5 | a policy number | what has been claimed against that policy before |
| `Retrieve Inspection Report` | step 3.1 | the claim number | a ready flag, and the report once it exists |
| `Client Notification` | steps 1.6, 6.3, 7.2 | subject, body, recipient; optionally `in_ClaimId` | a row in the tenant-level `ClaimCorrespondence` entity — the letter as sent |

### Every amount is in currency units, never cents

**Every money value the six return is in whole currency units of the claim's currency**: the claim form's lines and totals, the policy's limits, sublimits and deductible, the assessor's estimates, and the history's `paidTotal` and `paidByCoverage`. `4500` is four and a half thousand, not 45.00. If the case computes in integer cents, convert **once**, where each value enters the case, and test each converted copy against its source: a copied limit must equal the policy's figure, a prior claim's paid amount must equal the history's.

### Three shapes that are easy to get wrong

A mismatch here faults at run time having packed and deployed cleanly.

- **The extracted claim is an object, not a string.** An input declared `type: object` takes it directly.
- **The claim history is a string**, not an object — the opposite, in the same plan.
- **The three document outputs are job attachments.** Bind one to an attachment-typed input, never to a string.

## What each one does

**`Retrieve Property Claim`** generates a claim and uploads all three documents. `in_ClaimID` is the number stamped on them — pass your case's own external id so the case and the documents agree. `in_Scenario` and `in_Discrepancy` aim the run at a known problem; leave them empty for a random claim. `in_ProfileId` names one of the twelve claimant profiles (`claims-profile-01` … `claims-profile-12`) so two runs draw the same claimant, property, policy and damage figures — the reproducibility test; an unknown id faults. `in_Seed` (a non-zero integer) makes two runs of one profile produce identical documents; zero draws fresh, and the answer key records what was drawn. **`in_Scenario` is a closed list of five** — `random` · `auto-settle` · `eligibility-fail` · `review-fail` · `both-fail` — and anything else is not rejected, it just gives you a random claim. `in_Discrepancy` pins one exact injector by name, and those names come from the answer key, which `4-verify` tells you when you may read. Safe to call once per claim, and **it should not run again if a stage re-enters** — regenerating a claimant's documents mid-case is not a thing that happens in reality. An unknown `in_Discrepancy` faults and the fault text lists the valid ids; an unknown `in_Scenario` silently draws a random claim. **Why a generator, and why the case carries two test-only inputs for it:** a real engagement comes with sample claims from past cases; this exercise has none, so a generator stands in — and because a solution has to be tested against problems you can name, the generator takes the two arguments that plant one. Your case declares `scenario` and `discrepancy` as test-only inputs from the design onward, passes them through, and a production caller passes empty strings; they are not a shortcut, they are how the build is measured.

Its `out_ClaimID` is the file it wrote, which is the number you passed in. **You almost certainly should not bind it** — binding it to your own claim identifier gives that value two sources, and the one you did not intend wins whenever they differ.

**`Extract Claim Data (IXP)`** reads the claim form and runs the extraction model over it. **Only the claim form is extracted** — the policy and the assessor's report are prose and are read as documents (`PDD.md` §5.6).

**The extracted payload is deeply nested, and a bare binding path resolves one level.** Every group is an array and every field is an object:

```
ClaimClaimant[0].EmailAddress.Value                group → array, field → { Value, Confidence, OcrConfidence }
ClaimClaimTotals[0].TotalClaimAmount.Value.Value   money nests once more: .Value.Value and .Value.Currency
```

**The keys are the model's, not the labels'.** They are the taxonomy's labels with the spaces removed and every word capitalised — `Type of Incident` is `TypeOfIncident` (capital O, never `TypeofIncident`), `Present At Incident` is `PresentAtIncident`. A design that lower-cases the inner word binds fields that do not exist and finds out at `3e-run`. Read from a live payload (the `live` tag), the shared project emits exactly these:

| Group | Fields |
|---|---|
| `Claim` | `ClaimID` · `InsurerName` · `InsurerAddress` · `DateOfSubmission` |
| `ClaimClaimant` | `Name` · `PhoneNumber` · `EmailAddress` · `PolicyNumber` |
| `ClaimProperty` | `StreetAddress` · `City` · `State` · `ZipCode` · `PrimaryResidence` · `PresentAtIncident` |
| `ClaimIncident` | `DateOfIncident` · `TimeOfIncident` · `TypeOfIncident` · `DescriptionOfIncident` · `PoliceReportFiled` · `PoliceReportNumber` · `EmergencyServicesCalled` · `TemporaryRepairsMade` · `TemporaryRepairsDescription` |
| `ClaimDamageInventory` | `Category` · `Location` · `Description` · `EstimatedCost` (money — nests `.Value.Value` / `.Value.Currency` like the totals) · `RepairOrReplace` — one array element per item |
| `ClaimClaimTotals` | `TotalStructureDamage` · `TotalPersonalProperty` · `TotalAdditionalLivingExpenses` · `TotalClaimAmount` — money, so `.Value.Value` and `.Value.Currency` |

**Three value shapes no label tells you**, all from the same payloads: **booleans arrive as the strings `"Yes"` / `"No"`**, never JSON booleans — truthiness on `"No"` is true, so a rule tests the string; **dates arrive as `"2026-07-28T00:00:00"`**, ISO at midnight with no zone — and on a day-first form the model can swap day and month (`06/09/2026` read as 9 June), so a date that decides a rule is cross-checked against the one the claimant's own account states; and the confidence pair carries **three states, not two**: both `>= 0` is *read off the page*; `Confidence >= 0` with **`OcrConfidence: -1.0`** is *inferred, not on the page* — **and that marker is not reliable**: the two checkbox fields (`PrimaryResidence`, `PresentAtIncident`) come back with `OcrConfidence` 1.0 on one form and -1.0 on another whose checkbox is drawn identically, so treat both as model inference whatever the marker says, and build no provenance or threshold rule on `OcrConfidence`; **both `-1.0` with `Value: ""`** is *nothing found* (a blank ZIP row on a Hong Kong address) — a threshold rule that special-cases only `OcrConfidence` reads that as a very low score and flags an empty optional field as a data problem. Every field is `{ Value, Confidence, OcrConfidence }`; money nests once more (`.Value.Value`, `.Value.Currency`). A payload with four damage rows stringifies to about 5,000 characters, five to about 5,600 (`JSON.stringify` with no spacing — Python's `json.dumps` defaults add ~360); the damage inventory costs about **500 per row**, and the form has exactly five numbered rows, so 5,600 is the ceiling.

`3a-extraction/check_extraction_keys.py` walks every path the design reads against a saved payload.

So **anything the case itself has to read — above all the claimant's contact details for step 1.6 — has to be surfaced as a plain scalar by whatever step produces it.** A bare binding that reaches into the raw payload fails on every claim, loudly, on a required argument; an optional-chained `=js:` path with a wrong key fails **silently**, yielding nothing three blocks later — which is what `3a-extraction/check_extraction_keys.py` is for. Which step surfaces it is your design decision; that it must be surfaced is not.

**`Retrieve Policy Document`** fetches the policy by number, so it cannot run before extraction — the number comes from the claim form. That single dependency is most of why Intake has the shape it does.

**`Retrieve Previous Claims`** returns the claim history for a policy, as a JSON string; each `priorClaims[]` entry carries what it paid as `paidTotal` and `paidByCoverage`, not `paid`. **An empty history is a result, not a failure** (`PDD.md` step 1.5). **A history that says it is unavailable is not an empty one**: when Claims History does not answer, the document carries the policy number, `"status": "unavailable"` and a message, and no `priorClaims` — unreadable, flagged, and never read as zero (`PDD.md` B-05).

**`Retrieve Inspection Report`** fetches the assessor's report. **It does not fail when the report is not there yet** — it returns `out_ReportReady: false` and no file, which is what makes a waiting stage possible: call it, test the flag, move on or wait and call again. Treat anything other than an explicit `true` as not-ready.

**How long "not yet" lasts is decided by your poll interval, not by the assessor.** The stand-in models no timer: **every call is an independent draw, ready about four times in five.** Expected wait is roughly one and a quarter calls, and the wall clock is whatever you multiply that by. There is nothing to wait *for* — pick a short interval.

**`Client Notification`** takes a subject, a body and a recipient, **writes them to the job log and records the letter as one row in the tenant-level `ClaimCorrespondence` entity** (`seat`, `claimId`, `sentAt`, `recipient`, `subject`, `body`, `jobKey`, `folderKey`). It does not send email, and no email connection is provisioned. Bind the letter you would have sent; it is then visible in the log, on the record's correspondence thread, and to `4-verify`. **Put the claim reference in every subject line — `[PCL-…]` — and bind `in_ClaimId` where you have it:** the row is keyed by claim id, taken from `in_ClaimId` when bound and otherwise from the first `PCL-` reference in the subject, then the body. The seat and folder the automation records come from the job itself; nothing else is yours to pass. .

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
