# The provided processes — the plumbing contract

Six processes are deployed in your folder before you start. **They are infrastructure the exercise provides**:
you bind them, you never open or rebuild them. Together they cover every movement of a file or a payload between
storage and your case, which is why building one yourself is always a mistake — if you are about to write a
bucket download, an IXP invocation or a PDF-to-text step, it already exists.

**The argument names and types below are a contract.** Your case plan binds to them by name, and a wrong type is
the single most common way a claim faults at run time having packed and deployed cleanly.

## The six

| Process | In | Out |
|---|---|---|
| `Retrieve Property Claim` | `in_ClaimID` · `in_Scenario` · `in_Discrepancy` | — |
| `Extract Claim Data (IXP)` | `in_ClaimID` | `out_PolicyID` · `out_ClaimIXPDataJSON` · `out_ClaimFormPDF` |
| `Retrieve Policy Document` | `in_PolicyID` | `out_PolicyPDF` |
| `Retrieve Previous Claims` | `in_PolicyID` | `out_PreviousClaimsJSON` |
| `Retrieve Inspection Report` | `in_ClaimID` | `out_AssessmentReport` · `out_ReportReady` |
| `Client Notification` | `in_Subject` · `in_Body` · `in_Recepient` | — |

### Types, and the two that are easy to get wrong

| Argument | Type | Notes |
|---|---|---|
| `out_ClaimIXPDataJSON` | **object** | Not a string. An agent input declared `type: object` receives it directly; wrap or stringify it and the agent faults on input validation. |
| `out_PreviousClaimsJSON` | **string** | Not an object — the opposite of the one above, in the same case plan. Parse it where you need fields. |
| `out_ClaimFormPDF` · `out_PolicyPDF` · `out_AssessmentReport` | **file** | These become job attachments. Bind one to an agent input declared as a job attachment; never to a string. |
| `out_PolicyID` | string | The policy number read off the claim form. |
| `out_ReportReady` | boolean | `false` until the assessor's report exists. See the polling note below. |

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

**`Retrieve Policy Document`** fetches the policy PDF by policy number. So it cannot run before extraction — the
policy number comes from the claim form. That dependency is the reason Intake has the shape it does.

**`Retrieve Previous Claims`** returns the claim history for a policy, as a JSON string. Used by the analyses
that care whether this claimant has claimed before.

**`Retrieve Inspection Report`** fetches the assessor's report for a claim. **It does not fail when the report is
not there yet** — it returns `out_ReportReady: false` and no file. That is what makes a waiting stage possible:
call it, test the flag, and either move on or wait and call again. Treat any value other than an explicit `true`
as not-ready.

**`Client Notification`** takes a subject, a body and a recipient, and **writes them to the job log — it does not
send email.** No email connection is provisioned, deliberately: what this exercise cares about is the *content*
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
