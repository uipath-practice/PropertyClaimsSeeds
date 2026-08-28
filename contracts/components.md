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
| `SettlementCalculation` | what is payable, line by line, and every cap that bound it — from the assessor's report, the policy's limits and deductible, the claim history against the annual aggregate, the claim itself, **and `CoverageAnalysis`'s per-item verdict**: it computes over what §7.3 said is covered, it never re-decides coverage (measured 2026-08-27: two independent readings of one policy disagreed by 35,000 HKD), so it runs after coverage, not beside it | §7.4, `BR-20`–`BR-29` |
| `CredibilityAssessment` | whether the claim reads as told straight | §7.5, `BR-30`–`BR-33` |
| `DecisionRecommendation` | the outcome, and what an adjuster's override does to it | §7.6 and §7.8, `BR-40`–`BR-45`, `BR-60`–`BR-62` |
| `ClaimantCorrespondence` | what the claimant is told, and when | §7.7, `BR-50`–`BR-52` |

**§7.9 belongs to all seven.** It says what is *not* a finding, and a component that skips it flags something on every claim.

**Two of the seven do rule-expressible work, on purpose.** `PDD.md` §5.3 marks step 4.3 (the settlement arithmetic) and step 5.1 (the decision rules) rule-expressible, and the method would put them on a deterministic runner. They are agents here so the build has one component type and the day has one problem. Three things make that a considered trade rather than a careless one — and the first is **necessary, not sufficient**: `temperature` is `0` (`CONFIG.md`), yet measured 2026-08-27 the same settlement on the same six inputs paid 200,000 then 165,000 HKD on consecutive runs, the whole gap one policy clause read two ways. What made it reproduce was **a deterministic rule for every ambiguous case** — the test for *capable of two readings* is mechanical: if deciding a row means weighing what a word in the policy *means*, two readings exist and the row is paid (`BR-16`); after that five runs matched on all 34 numeric fields. And `4-verify` re-runs the clean claim and compares **every figure to the cent — not the prose, which still varies while the numbers hold**. `check_sdd.py` warns rather than fails on these two (`NATURE-1`).

**All seven are low-code agents — an `agent.json` built with Agent Builder**, not a coded framework. Temperature is **0** — the settlement and decision agents must reproduce their numbers. The model is yours to choose: the newest generally-available Anthropic Sonnet the tenant offers (`uip agent model list`), named once in `sdd.md` §4 and on all seven; changing it after 3c is a contract change and is logged. (`CONFIG.md` pins neither — two measured designs went looking for a pin that was not there.)

**None of the seven has custom tools, memory, or evaluation sets.** Four carry the platform's built-in **Analyze Files** tool (`analyze-attachments`, `resources/Analyze Files/resource.json` — the folder named after the resource, spaces included), because a `job-attachment` input renders only `ID`, `FullName`, `MimeType` and `Metadata` into the prompt and the document's contents reach the model through that tool alone (measured 2026-08-27: without it, every document check is *unresolvable* on every claim). That is how an input is read, not a tool in the sense pinned here — nothing is built and the case provides nothing for it. Nothing is remembered between claims, and the state store is the claim record. Evaluation sets make an agent self-test against mock inputs; this solution is tested end to end against real claims instead, at `4-verify`.

**A prompt governs what an agent reports, not what it concludes.** Measured 2026-08-27 across twelve deploys: four prompt revisions could not stop a component escalating on a check no injector ever plants, and one condition in the case did; six revisions could not make another component see a planted impossibility that sat inside a four-read envelope (1 in 13 caught). Where a conclusion decides whether a claim reaches a human, put it in a case condition. The credibility section is the worked example: BR-30–33 stay one component and stay soft — four reads that together produce **one risk level, low / medium / high** — and the *routing* is not the component's to decide: the case sends medium or high to the adjuster's gate whatever the recommendation says (`PDD.md` BR-44). The component estimates; the condition routes; the human decides.

**One agent per area, never one per check.** `EligibilityScreening` reports all five of its checks in one envelope; five agents reporting one check each is the same work, five times the binding, and a reviewer reading five findings where the process has one.

## And one app — an Action app, not a standalone one

The two human decisions are answered in a **Coded Action App**: it opens inside Action Center against a task the case raised, and a reviewer works **one claim at a time**. `CONFIG.md` pins its name. It is created at `3d` **beside the solution** with its contract and an empty page, published and deployed by its own command into the seat folder (`CONFIG.md`, *Deploying*), and its screens are built at `3f` — against payloads your own Agents actually produced — and redeployed alone.

**It is not a dashboard.** A standalone app listing claims in flight, closed-today counts and straight-through rates is `PDD.md` §11's reporting view — a separate, later deliverable. A design that gives the reviewer's screen a claims list and a portfolio of routes has built the wrong thing.

| | |
|---|---|
| Contract | **`review-task.md`** — what the case hands it and what it hands back. Bound at `3d-case`, before its screens exist |
| Framework | **React + TypeScript**, with `@uipath/uipath-typescript` for platform calls |
| Screens | **two** — one per gateway, and they differ only in what has happened by the time each opens. **No router**: a task opens one claim, and there is nowhere else to go |
| What each shows | **`PDD.md` §5.7, and not a summary.** H1: the five screening checks with their reasons, passes included, and the claim form and policy. H2: every stage-4 finding side by side, the recommendation with every reason and its confidence, the three documents, and **the settlement line by line** — claimed, payable, the section it fell under, the cap, deductible or aggregate remainder that reduced it (§7.4), prior claims' erosion, the net |
| What the adjuster may change | any settlement line, up or down, within §7.8: never above the higher of the claimed amount and the assessor's estimate for that line, never above its cap, always with a reason; the recommendation itself is never mutated. The confirmed settlement goes back as a task output — `review-task.md` |
| State | **no client store.** The claim record is the single source of truth; the Action App reads it and returns a decision, and the case does the writing |

## Everything else already exists — bind it, do not build it

**The case plan's own task types are the whole toolbox.** Connector activities read and write the claim record, `=js:` expressions derive values and test conditions, `wait-for-timer` waits, `action` tasks ask a human, `process` tasks call the six automations. A design that adds a component to do any of those — a retrieval workflow, a record writer, a payload normaliser, a "tool" for an agent — has not read this table, and it costs a project to build, publish, version, bind and debug.

| Work | What does it | Never |
|---|---|---|
| generating a claim, extraction, policy, claim history, inspection report, notifying the claimant | the **six provided automations**, `provided-processes.md` | a new RPA process |
| writing the claim record | **`execute-connector-activity`** tasks in the case — `claim-entity.md`, *The case writes this itself* | a writer component |
| reading the claim record — for a later stage, a condition, or the reviewer's screen | the same connector's **read** activities (`GetEntityRecord`, `QueryEntityRecords`) in the case; the app reads it by id | a retrieval workflow, or a "tool" an agent calls |
| reading a nested payload, deriving a scalar, testing a condition | a **`=js:` expression** in the case, with optional chaining | a normaliser component |
| the two human decisions | **`action`** tasks, answered in the Coded Action App | anything else |
| waiting for the assessor | a **`wait-for-timer`** task and a re-call of the provided process | a polling component |

**No new API Workflows and no new RPA processes.** If a step seems to need one, the answer is almost always a case expression or a provided automation you have not read yet. The proven build of this solution has none, and paying the settlement is out of scope (`PDD.md` OS2) — this process authorises an amount and hands it over.

## The one thing this does not pin

**How the case is shaped is still yours** — stages, task order, entry and exit conditions, what runs in parallel, where each write lands, which SLAs apply. That is the design work, and it is where the interesting decisions are. What is pinned is the inventory, so that every seat spends its day on the same problem.
