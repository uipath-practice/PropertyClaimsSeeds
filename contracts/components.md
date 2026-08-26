# What you build, and what is already there

**You build seven agents. Nothing else.** Every other piece of this solution already exists, and the case plan's job is to wire them together.

**Pinned, and it is worth knowing why.** The design would normally choose this, and choosing it badly is expensive in a way that is invisible until late: a design that names a component per rule produces twenty projects instead of eight, each to build, publish, version, bind and debug, and no two seats end up comparable. Two builds measured on the same PDD produced nineteen components and a different nineteen. **Design the split yourself if you want the exercise, then reconcile against this before you build anything.**

## The seven

One per `PDD.md` §7 section, which is where the split comes from — the process already groups its own rules, and that grouping is the component boundary.

| Agent | Decides | Owns |
|---|---|---|
| `EligibilityScreening` | whether the claim is worth investigating at all | §7.1, `BR-01`–`BR-05` |
| `AssessmentReportValidation` | whether the assessor's report can be relied on | §7.2, `BR-06`–`BR-09` |
| `CoverageAnalysis` | what the policy covers, item by item | §7.3, `BR-10`–`BR-16` |
| `SettlementCalculation` | what is payable, line by line, and every cap that bound it | §7.4, `BR-20`–`BR-29` |
| `CredibilityAssessment` | whether the claim reads as told straight | §7.5, `BR-30`–`BR-33` |
| `DecisionRecommendation` | the outcome, and what an adjuster's override does to it | §7.6 and §7.8, `BR-40`–`BR-45`, `BR-60`–`BR-62` |
| `ClaimantCorrespondence` | what the claimant is told, and when | §7.7, `BR-50`–`BR-52` |

**§7.9 belongs to all seven.** It says what is *not* a finding, and a component that skips it flags something on every claim.

**One agent per area, never one per check.** `EligibilityScreening` reports all five of its checks in one envelope; five agents reporting one check each is the same work, five times the binding, and a reviewer reading five findings where the process has one.

## Everything else already exists — bind it, do not build it

| Work | What does it | Never |
|---|---|---|
| generating a claim, extraction, policy, claim history, inspection report, notifying the claimant | the **six provided automations**, `provided-processes.md` | a new RPA process |
| writing the claim record | **`execute-connector-activity`** tasks in the case — `claim-entity.md`, *The case writes this itself* | a writer component |
| reading a nested payload, deriving a scalar, testing a condition | a **`=js:` expression** in the case, with optional chaining | a normaliser component |
| the two human decisions | **`action`** tasks, answered in the validation app | anything else |
| waiting for the assessor | a **`wait-for-timer`** task and a re-call of the provided process | a polling component |

**No new API Workflows and no new RPA processes.** If a step seems to need one, the answer is almost always a case expression or a provided automation you have not read yet. The proven build of this solution has none, and paying the settlement is out of scope (`PDD.md` OS2) — this process authorises an amount and hands it over.

## The one thing this does not pin

**How the case is shaped is still yours** — stages, task order, entry and exit conditions, what runs in parallel, where each write lands, which SLAs apply. That is the design work, and it is where the interesting decisions are. What is pinned is the inventory, so that every seat spends its day on the same problem.
