# What you build, and what is already there

**You build seven agents and one app. Nothing else.** Every other piece of this solution already exists, and the case plan's job is to wire them together.

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

**All seven are low-code agents — an `agent.json` built with Agent Builder**, not a coded framework. `CONFIG.md` pins the model and temperature, which are fields in that file.

**None of the seven has tools, memory, or evaluation sets.** They are given their inputs on the task call and return a conclusion — no tool ever fires, nothing is remembered between claims, and the state store is the claim record. Evaluation sets make an agent self-test against mock inputs; this solution is tested end to end against real claims instead, at `4-verify`.

**One agent per area, never one per check.** `EligibilityScreening` reports all five of its checks in one envelope; five agents reporting one check each is the same work, five times the binding, and a reviewer reading five findings where the process has one.

## And one app — an Action app, not a standalone one

The two human decisions are answered in a **Coded Action App**: it opens inside Action Center against a task the case raised, and a reviewer works **one claim at a time**. `CONFIG.md` pins its name. You build it at `3f-validation`, after the case runs, because it is built against payloads your own components actually produced.

**It is not a dashboard.** A standalone app listing claims in flight, closed-today counts and straight-through rates is `PDD.md` §11's reporting view — a separate, later deliverable. A design that gives the reviewer's screen a claims list and a portfolio of routes has built the wrong thing.

| | |
|---|---|
| Framework | **React + TypeScript**, with `@uipath/uipath-typescript` for platform calls |
| Screens | **two** — one per gateway, and they differ only in what has happened by the time each opens. **No router**: a task opens one claim, and there is nowhere else to go |
| State | **no client store.** The claim record is the single source of truth; the screen reads it and returns a decision, and the case does the writing |

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
