# The provided processes — the plumbing contract

Six processes are deployed in your folder before you start. You bind them; you never open or rebuild them.

**They are the integration layer.** In a real insurer, retrieving a policy means logging into a portal,
searching, downloading a PDF and handing it back — and the same for the assessor's report and the claim history.
Here that is stood in with a storage bucket, which keeps the shape while removing a dependency nobody can
provision for a room full of people. The interfaces are what they would be either way: ask for a policy by
number, get a file.

So what is left for you is the part that is actually hard, and actually transferable: **stitching these into a
case, putting a human in the right two places, and making it survive an execution that runs for days.**

Practically: if you are about to write a bucket download, an IXP invocation or a PDF-to-text step, stop — it
already exists, and it is on the list below.

**The argument names and types below are a contract.** Your case plan binds to them by name, and a wrong type is
the single most common way a claim faults at run time having packed and deployed cleanly.

## Read the contract from the platform, not from here

**This file explains what each process is for. The platform is authoritative on its arguments**, and you should
read them before you bind anything:

```bash
uip or processes list --folder-key <your seat folder> --output json     # what is deployed
uip or packages entry-points "<PackageId>:<Version>" --output json      # its exact I/O schema
```

`packages entry-points` returns real JSON Schema for inputs and outputs — names, types, which are required, and
each argument's own description. That is the shape your case plan has to match, and it cannot go stale the way
a document can.

Two habits worth forming here, because they apply to everything you bind later: **check what is actually
deployed rather than what you were told**, and **treat a document as the explanation and the platform as the
truth.** If this file and `entry-points` disagree, the platform wins — and that disagreement is a finding worth
logging.

`uip maestro case tasks describe --type process` looks like the right command and does **not** work for these —
it accepts `process` and then reports no entry found. Use `packages entry-points`.

## The six, and what each is for

| Process | Stands in for | Give it | Get back |
|---|---|---|---|
| `Retrieve Property Claim` | a claim arriving through the front door | a claim number, and optionally an aimed scenario | the documents land in the buckets; it also echoes `out_ClaimID` |
| `Extract Claim Data (IXP)` | reading the submitted form | the claim number | the claim as structured data, the policy number, and the form as a file |
| `Retrieve Policy Document` | the policy admin system | a policy number | the policy document |
| `Retrieve Previous Claims` | the claims history system | a policy number | what has been claimed against that policy before |
| `Retrieve Inspection Report` | the assessor's filing | the claim number | a ready flag, and the report once it exists |
| `Client Notification` | correspondence to the claimant | subject, body, recipient | nothing |

### Three shapes that are easy to get wrong

Check them against `packages entry-points`; they are called out because a mismatch fails at run time rather than
at bind time.

- **The extracted claim is an object, not a string.** An agent input declared `type: object` takes it directly.
- **The claim history is a string**, not an object — the opposite, in the same case plan.
- **The three document outputs are job attachments.** Bind one to an attachment-typed agent input, never to a
  string.

## What each one does

**`Retrieve Property Claim`** generates a claim and uploads all three documents. `in_ClaimID` is the claim number
you want stamped on them — pass your case's own external id, so the case and the documents agree. `in_Scenario`
and `in_Discrepancy` aim the run at a known problem and are how block 7 tests; leave them empty for a random
claim. It produces no outputs: the documents are its output, and they land in the buckets.

It is safe to call once per claim and should not run again if a stage re-enters — regenerating a claimant's
documents mid-case is not a thing that happens in reality.

**`Extract Claim Data (IXP)`** reads the claim form from storage and runs the extraction model over it. This is
the only document that gets extracted; the policy and the assessor's report are prose and are read by an analysis
instead (`pdd.md` §1). Its three outputs are the extracted claim, the policy number found on it, and the claim
form itself as a file.

**`Retrieve Property Claim`** generates the three documents into the buckets. It returns one output,
`out_ClaimID` — the name of the file it wrote to the `Claims` bucket, which is the claim number you passed in.
**You almost certainly should not bind it.** The claim id is the case's own external id
(`=js:metadata.ExternalId`); binding this output to your `claimId` variable gives that value two sources, and the
one you did not intend wins whenever they differ. An earlier version of this document said the process produced
no outputs at all, which was simply wrong.

**`Retrieve Policy Document`** fetches the policy PDF by policy number. So it cannot run before extraction — the
policy number comes from the claim form. That dependency is the reason Intake has the shape it does.

**`Retrieve Previous Claims`** returns the claim history for a policy, as a JSON string. Used by the analyses
that care whether this claimant has claimed before.

**`Retrieve Inspection Report`** fetches the assessor's report for a claim. **It does not fail when the report is
not there yet** — it returns `out_ReportReady: false` and no file. That is what makes a waiting stage possible:
call it, test the flag, and either move on or wait and call again. Treat any value other than an explicit `true`
as not-ready.

**`Client Notification`** takes a subject, a body and a recipient, and **writes them to the job log — it does not
send email.** Its recipient argument is spelled **`in_Recepient`**, with the `i` and the `e` transposed. That is
a typo in our process, not in this document; bind the spelling the platform reports, and read the arguments from
`packages entry-points` rather than from any prose — including this paragraph.

**Where the recipient comes from**, since no column holds it: the claimant's email address is in the raw
extraction payload, as the `ClaimClaimant` group's email field. It is not promoted to a claim-record column
because nothing downstream reads it twice — the notification tasks are its only consumer. Pull it from the
extraction blob at the point of use. No email connection is provisioned, deliberately: what this exercise cares about is the *content*
of what the claimant is told, which an analysis produces and `pdd.md` §7 governs. Bind the letter you would have
sent; it is then visible in the log and recorded on the claim.

## Where the files live

Three buckets, in your folder. Knowing the naming lets you check by hand what a run produced:

| Bucket | Holds |
|---|---|
| `Claims` | `<claimId>-claim.pdf`, and the policy's history as `<policyId>-history.json` |
| `Insurance Policies Repository` | `<policyId>.pdf` |
| `Assessor Reports` | `<claimId>-incident-report.pdf` |

The claim history is keyed by **policy**, not by claim, and lives in the `Claims` bucket with the claim forms —
worth knowing before you go looking for it somewhere else.

**`Claims` also holds a `manifest.json` per claim. Nothing you build may read it.** It states which problems were
planted and what the outcome should be; it is the test oracle and it is yours in block 7 only.

## The one thing that will bite you

**These processes live in your seat folder, not in your solution's folder.** Deploying a solution creates a
sub-folder, and a sub-folder does not inherit its parent's processes. So every binding to one of these needs its
folder named explicitly — `CONFIG.md` says which.

Get it wrong and the case faults about five seconds in, with *"the job's associated process could not be
found"*, having executed nothing. The message names the process; the problem is the folder it was looked for in.
