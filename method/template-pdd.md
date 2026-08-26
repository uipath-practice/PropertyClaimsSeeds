<!--
PDD SKELETON — copy this file to `docs/pdd.md` and fill it in.

Placeholder conventions:
  <UPPER_SNAKE_IN_ANGLES>  replace with a real value
  [SME REVIEW]             a business-knowledge gap; must be answered before sign-off
  [DEFAULT]                an industry-standard assumption applied; confirm before production
  > None.                  use this when a section genuinely does not apply — never delete the heading

Delete every HTML comment block before circulating for sign-off.

BOUNDARY REMINDER — this document describes the BUSINESS, not the platform. Do not put
product/technology selection, agent configuration, prompts, selectors, schemas, entity
definitions, or connection details here. Those belong in the SDD.

Per-section guidance is in pdd-guide.md. The one column worth reading about before you
start is §5.3's Decision nature — it is what lets this document drive an architecture
rather than merely describe a process.
-->

# Process Definition Document — <PROCESS_NAME>

**Client / business unit:** <CLIENT_OR_BU>
**Document owner:** <BUSINESS_ANALYST_NAME>
**Status:** Draft | In Review | Signed
**Version:** <N.N>
**Date:** <YYYY-MM-DD>

---

## Document History

| Version | Date | Author | What changed |
|---|---|---|---|
| 0.1 | <YYYY-MM-DD> | <NAME> | Initial draft |

## Sign-off

Signing this document confirms that the business behaviour described here is correct and complete. Changes after sign-off go through §15 Change Control.

| Role | Name | Date | Signature |
|---|---|---|---|
| Process Owner | <NAME> | | |
| Business sponsor | <NAME> | | |
| Business Analyst (author) | <NAME> | | |
| Solution Architect (reviewer) | <NAME> | | |

## Key Contacts

<!-- Only list roles that are actually named. Do not invent rows. -->

| Role | Name | Contact | Scope |
|---|---|---|---|
| Process Owner / SME | <NAME> | <EMAIL> | <WHAT_THEY_OWN> |
| Business Analyst | <NAME> | <EMAIL> | |
| Solution Architect | <NAME> | <EMAIL> | |
| Developer(s) | <NAME> | <EMAIL> | |
| Project Manager | <NAME> | <EMAIL> | |
| System owner — <SYSTEM> | <NAME> | <EMAIL> | Access, change windows |

## Glossary & Operational Vocabulary

<!-- Customer's exact words and exact casing. Synonym drift here becomes wrong stage/task/persona names downstream. -->

| Term | Exact form used by the business | Meaning | Never call it |
|---|---|---|---|
| <TERM> | <VERBATIM_FORM> | <MEANING> | <SYNONYM_TO_AVOID> |

**Decision outcome labels (verbatim):** <OUTCOME_1> · <OUTCOME_2> · <OUTCOME_3>
**Role titles (verbatim):** <ROLE_1> · <ROLE_2>
**System short names (verbatim):** <SYSTEM_1> · <SYSTEM_2>

## Authoritative References

| # | Source | Type | Claim class | Stability / review date |
|---|---|---|---|---|
| R1 | <DOCUMENT_OR_REGULATION> | Policy / Regulation / SOP / Interview / Recording | Statutory requirement \| Supervisory guidance \| Industry practice \| Example internal policy | <DATE> |

---

## 1. Purpose and Business Case

### 1.1 Purpose of this document
<ONE_PARAGRAPH — what decision this document supports and who consumes it.>

### 1.2 Business objective and target outcome
**Outcome:** <ONE_SENTENCE>
**Primary KPI moved:** <cycle time | manual effort | quality/accuracy | cost | throughput | compliance>
**Current baseline → target:** <BASELINE> → <TARGET>

### 1.3 Success criteria

| # | Criterion | Measure | Target |
|---|---|---|---|
| SC1 | Straight-through processing rate | % of items completed with no human touch | <N>% |
| SC2 | Cycle time | <UNIT> from trigger to close | <N> |
| SC3 | Accuracy | <HOW_MEASURED> | ≥ <N>% |
| SC4 | <CRITERION> | <MEASURE> | <TARGET> |

### 1.4 Business case

| Item | Value | Source |
|---|---|---|
| Volume per <PERIOD> | <N> | <SOURCE> |
| Average handling time (manual) | <N> <UNIT> | <SOURCE> |
| Fully loaded cost per <UNIT> | <VALUE> | <SOURCE> |
| Expected annual saving | <VALUE> | <CALCULATION> |
| Estimated build effort | <N> <UNIT> | <SOURCE> |

### 1.5 Minimum prerequisites for automation

| # | Prerequisite | Owner | Status |
|---|---|---|---|
| P1 | <LICENCE_OR_ACCESS> | <OWNER> | Confirmed \| Pending \| [SME REVIEW] |

---

## 2. Process Overview

### 2.1 Process profile

| Field | Value |
|---|---|
| Process full name (verbatim, if the business has a canonical one) | <NAME> |
| Function / department / division | <VALUE> |
| Short description (operation, activity, outcome) | <VALUE> |
| Business criticality | <High \| Medium \| Low> |
| SOx / regulated process | <Yes \| No> — <WHICH_REGIME> |
| Trigger — who or what starts it, and how it arrives | <VALUE> |
| Frequency and business hours | <VALUE> |
| Volume per period (range, and peak) | <MIN>–<MAX>; peak <N> during <WHEN> |
| Average handling time — today / target | <N> / <N> |
| FTE involved | <N> |
| Exception rate (estimate) | <N>% |
| Input data — what arrives, in what form, from where | <VALUE> |
| Output data — what leaves, in what form, to where | <VALUE> |
| Data sensitivity | <PII \| PHI \| payment \| none> |
| Must NOT appear in logs | <FIELDS> |
| Delivery model (where this will run) | <Automation Cloud \| Automation Suite <VERSION> \| standalone Orchestrator> |
| Products the client rules out, and why | <PRODUCT — REASON> \| none |

### 2.2 In scope

| # | Activity | Note |
|---|---|---|
| IS1 | <ACTIVITY> | |

### 2.3 Out of scope

<!-- Strictly enforced downstream: nothing here may appear in the SDD's component or workflow inventory. -->

| # | Activity | Reason |
|---|---|---|
| OS1 | <ACTIVITY> | Manual by policy \| Phase 2 \| No system access \| Low volume \| <OTHER> |

### 2.4 Assumptions and constraints

| # | Type | Statement | Impact if wrong |
|---|---|---|---|
| A1 | Business \| Organisational \| Timing \| Technical | <STATEMENT> | <IMPACT> |

---

## 3. Personas and Responsibilities

| Persona (verbatim) | What they do | Steps involved | Decision authority / thresholds | Touches per period | Must be able to see |
|---|---|---|---|---|---|
| <ROLE> | <RESPONSIBILITY> | <STEP_REFS> | <e.g. approves up to <AMOUNT>; above that → <ROLE>> | <N> | <DATA_THEY_NEED> |

<!-- Thresholds must be numeric and sit next to the role they gate. "Senior staff handle large cases" is unusable. -->

---

## 4. As-Is Process

### 4.1 As-is narrative
<NARRATIVE — how the work is done today, end to end.>

### 4.2 As-is process map
<DIAGRAM_OR_LINK — swimlane by persona where possible.>

### 4.3 Applications used today

| Application | Version | Interface type | Access method | System language | How a human authenticates | Quirks |
|---|---|---|---|---|---|---|
| <NAME> | <VER> | Web \| Desktop \| Terminal \| API \| Mobile | <URL_OR_PATH> | <LANG> | <METHOD> | <SPA / hash routing / session timeout / Citrix / VDI> |

### 4.4 Pain points and manual workarounds

<!-- Mark every step that exists ONLY because a human is doing the work. Those are meant to disappear in the to-be. -->

| # | Pain point / workaround | Step(s) | Exists only because a human does the work? | Impact |
|---|---|---|---|---|
| PP1 | <DESCRIPTION> | <STEP_REFS> | Yes \| No | <IMPACT> |

### 4.5 Volumetrics by step

| Step | Volume | Time per item | Total effort per period |
|---|---|---|---|
| <STEP> | <N> | <N> | <N> |

---

## 5. To-Be Process (business level)

### 5.1 To-be narrative
<NARRATIVE — what changes, what a human still does, where they enter the loop and what they decide.>

### 5.2 To-be process map
<DIAGRAM_OR_LINK — must match the numbered step list in §5.3 exactly. Keep step numbers stable across versions.>

### 5.3 Detailed step table

<!--
Action verbs — use this fixed set so each step can be placed on an executor:
collect · validate · decide · transform · create · transfer · notify · wait · assign · review · escalate · schedule · archive
Actor = a human role, or "system". Never "robot" or "agent" — that is a design decision.
Decision nature is the single most valuable column in this document.
-->

| Step | Action (verb + object) | Actor | System / data touched | Decision nature | Expected result | Remarks |
|---|---|---|---|---|---|---|
| 1.1 | <VERB> <OBJECT> | <ROLE \| system> | <SYSTEM> | Rule-expressible: <THE_RULE> \| Judgement: <WHAT_IS_WEIGHED> \| n/a | <WHAT_IS_TRUE_AFTER> | <EDGE_CASES> |
| 1.2 | | | | | | |

### 5.4 Control-flow structure

<!-- This subsection decides Maestro Case vs BPMN vs Flow vs long-running RPA. Absent structure must NOT be inferred — write "None" where it does not occur. -->

| Structure | Present? | Where, and what exactly happens |
|---|---|---|
| Parallel work that forks and rejoins | Yes \| No | <STEPS; all branches must finish \| first to finish wins> |
| Wait on an external event (message, document, signal) | Yes \| No | <WHICH_EVENT, FROM_WHERE> |
| Wait on a clock (timer, schedule, deadline) | Yes \| No | <CADENCE_OR_DEADLINE> |
| Per-step deadline or timeout | Yes \| No | <STEP → LIMIT → WHAT_HAPPENS_ON_EXPIRY> |
| Cancel or compensate earlier work on failure | Yes \| No | <WHAT_MUST_BE_UNDONE> |
| Reusable group of steps repeated in several places | Yes \| No | <WHICH_STEPS> |
| Handoff to a separate long-running process | Yes \| No | <WHICH_PROCESS> |
| Work arrives in batches vs item by item | Batch \| Per item | <DOES_ONE_FAILURE_BLOCK_OTHERS?> |

### 5.5 Lifecycle, stages and SLAs

**Stages**

| # | Stage (business name) | Owner | Considered done when | Required for overall completion | Exceptional / interrupting |
|---|---|---|---|---|---|
| 1 | <STAGE> | <ROLE> | <CONDITION> | Yes \| No | No |
| S1 | <EXCEPTION_LANE> | <ROLE> | <CONDITION> | No | Yes — can interrupt from <WHERE> |

**SLAs**

| Scope | Duration | At-risk threshold | At-risk action | Breach action |
|---|---|---|---|---|
| Whole work item | <N> <hours \| days> | <N>% | Notify <ROLE> \| Open <LANE> | Notify <ROLE> \| Open <LANE> |
| Stage: <STAGE> | <N> <UNIT> | <N>% | <ACTION> | <ACTION> |

**Exit paths — every one, not just the happy path**

| # | Exit | When it happens | Counts as completed? |
|---|---|---|---|
| E1 | Normal completion | <CONDITION> | Yes |
| E2 | <Withdrawn \| Denied \| Duplicate \| Transferred out \| …> | <CONDITION> | No |

### 5.6 Documents and unstructured input

| Document type | How it arrives | Structure | Fields that must be read | Human confirmation needed? | Layout variability | Change frequency | Where stored |
|---|---|---|---|---|---|---|---|
| <TYPE> | <CHANNEL> | Structured \| Semi-structured \| Free-form | <FIELDS> | Yes \| No | <Low \| Medium \| High> | <FREQUENCY> | <LOCATION — never assume> |

### 5.7 Human decision and approval points

<!-- Business intent, not a form spec. Name every outcome. Do not specify field layouts. -->

| # | Touchpoint | Who decides | What they need to see | What they may change | Outcomes (every button) | What each outcome causes | Delegable? | If nobody acts within the SLA |
|---|---|---|---|---|---|---|---|---|
| H1 | <NAME> | <ROLE> | <INFORMATION> | <EDITABLE_ITEMS> | <OUTCOME_1> / <OUTCOME_2> / <OUTCOME_3> | <CONSEQUENCE_EACH> | Yes \| No | <BEHAVIOUR> |

---

## 6. Data

### 6.1 Data objects

| Object | What it represents | Business identifier | Lifecycle | Owner | System of record |
|---|---|---|---|---|---|
| <OBJECT> | <MEANING> | <ID_FORMAT> | <STATES> | <ROLE> | <SYSTEM> |

### 6.2 Data fields per object

<!-- Business meaning only. No storage technology, no types like STRING/DECIMAL, no relationships, no choice-set IDs. -->

**Object: <OBJECT_NAME>**

| Field (business name) | Meaning | Required | Valid values / range | Format | Source system | Process reads / writes |
|---|---|---|---|---|---|---|
| <FIELD> | <MEANING> | Yes \| No | <VALUES> | <FORMAT> | <SYSTEM> | Read \| Write \| Both |

### 6.3 Value mappings

**<MAPPING_NAME> — <SOURCE_SYSTEM> → <TARGET_SYSTEM>**

| Source value | Target value | Note |
|---|---|---|
| <VALUE> | <VALUE> | |

### 6.4 Retention, privacy and residency

| Requirement | Detail | Source |
|---|---|---|
| Retention period — records | <N> <UNIT> | <POLICY> |
| Retention period — documents | <N> <UNIT> | <POLICY> |
| Fields to mask / redact | <FIELDS> | <POLICY> |
| Fields that must never be logged | <FIELDS> | <POLICY> |
| Data residency limit | <REGION> | <POLICY> |

---

## 7. Business Rules

| ID | Rule (`When … if … then …`) | Applies at step | Inputs it reads | Outcome | Source / authority | Policy or regulatory | Example (input → expected output) |
|---|---|---|---|---|---|---|---|
| BR-01 | <RULE> | <STEP> | <FIELDS> | <OUTCOME> | <REF> | Policy \| Regulatory | <CONCRETE_INPUT> → <CONCRETE_OUTPUT> |

<!-- A worked example turns a rule into a test oracle. Thresholds: state the comparator and the number, next to the role or action they gate. -->

---

## 8. Exceptions and Error Handling

### 8.1 Business exceptions

| ID | Name | Detected at step | How it is detected | What should happen | Who is notified | Can the item continue? |
|---|---|---|---|---|---|---|
| B-01 | <NAME> | <STEP> | <CONDITION> | <ACTION> | <ROLE> | Yes \| No |
| B-99 | Any other business exception | any | — | <CATCH_ALL_ACTION> | <ROLE> | No |

### 8.2 Known technical / system exceptions

| ID | Name | Detected at step | Business expectation | Who is notified |
|---|---|---|---|---|
| E-01 | <NAME> | <STEP> | Retry \| Park \| Escalate | <ROLE> |

### 8.3 Unknown exceptions
**Owner of an unclassified failure:** <ROLE>
**Must be visible within:** <TIME>
**Is it safe to leave the item parked?** <Yes \| No> — <WHY>

### 8.4 Reversibility and risk

| Step | Irreversible effect | Requires a human gate? |
|---|---|---|
| <STEP> | <EFFECT — payment issued, letter sent, regulatory filing> | Yes |

---

## 9. Integrations and System Landscape

| System | Role in this process | Direction | API exists? | Reachable from cloud? | Machine-local data involved? | Owner | Notes |
|---|---|---|---|---|---|---|---|
| <SYSTEM> | <ROLE> | Inbound \| Outbound \| Both | Yes \| No \| Unknown [SME REVIEW] | Yes \| On-prem only \| Unknown | Excel / file share / desktop app / local DB / terminal — or none | <OWNER> | |

**Inbound events**

| Event | Source system | What it means | Correlation key back to the work item |
|---|---|---|---|
| <EVENT> | <SYSTEM> | <MEANING> | <KEY> |

---

## 10. Compliance and Control Requirements

| # | Requirement | Source regulation / policy | Steps constrained | Evidence that must be produced | Auditor | Jurisdiction |
|---|---|---|---|---|---|---|
| C1 | <REQUIREMENT> | <SOURCE> | <STEPS> | <EVIDENCE> | <ROLE> | <REGION \| all> |

**Architecture-shaping controls:** mandatory human review at <STEPS> · segregation of duties between <ROLE> and <ROLE> · audit trail must contain <CONTENTS> · four-eyes check on <STEP> · data residency limited to <REGION>.

---

## 11. Reporting and Monitoring Requirements

| # | Report / view | Frequency | Content | Audience | Where it is viewed |
|---|---|---|---|---|---|
| RP1 | <NAME> | Real-time \| Daily \| Weekly \| Per run | <FIELDS_AND_AGGREGATES> | <ROLE> | <TOOL> |

**In-flight visibility needed:** <work queue \| SLA dashboard \| ageing view \| none>

---

## 12. Process Variants and Regional Forks

| # | Variant-defining question | Possible answers | What differs |
|---|---|---|---|
| V1 | <QUESTION — line of business / jurisdiction / channel / segment / value band> | <ANSWERS> | <DIFFERENCES> |

**Base process in §5 assumes:** <WHICH_VARIANT>

---

## 13. Test Data and Canonical Examples

### 13.1 Canonical case — complete

<!-- Real-shaped values. If masking is required, keep the shape (CLM-2026-0001842, not <claim number>). -->

| Field | Value |
|---|---|
| <FIELD> | <CONCRETE_VALUE> |

**Accompanying documents:** <FILENAMES_IN_APPENDIX_B>

**Expected outputs**

| Decision point / output | Expected value |
|---|---|
| <POINT> | <CONCRETE_VALUE> |

### 13.2 Examples per rule and exception path

| Rule / exception ID | Input | Expected outcome |
|---|---|---|
| BR-01 | <INPUT> | <OUTCOME> |
| B-01 | <INPUT> | <OUTCOME> |

### 13.3 Test environment and data availability
**Where test data comes from:** <SOURCE>
**Test environment:** <ENVIRONMENT> — access owner <ROLE>
**Cleanup expectation after test runs:** <EXPECTATION>

---

## 14. Out of Scope for Automation

| # | Step / activity | Category | Reason |
|---|---|---|---|
| N1 | <STEP> | Policy requires a human \| Volume too low \| System inaccessible \| Later phase | <REASON> |

---

## 15. Change Control

| # | Date | Change | Sections affected | Reason | Raised by | Impact class |
|---|---|---|---|---|---|---|
| 1 | <YYYY-MM-DD> | <CHANGE> | <SECTIONS> | <REASON> | <NAME> | Business change (re-sign-off) \| Clarification (no re-sign-off) |

---

## Appendices

### A — Screenshots
<!-- PNG/JPG only. .emf/.wmf pasted from Office cannot be read by tooling. Annotate each: which application, which screen, what to notice. -->

| # | Application | Screen | What to notice |
|---|---|---|---|
| A1 | <APP> | <SCREEN> | <FIELDS_OR_VALUES_OF_INTEREST> |

### B — Sample documents

| # | Document type | Filename | Redacted? |
|---|---|---|---|
| B1 | <TYPE> | <FILENAME> | Yes \| No |

### C — Sample data files

| # | Content | Filename | Format |
|---|---|---|---|
| C1 | <CONTENT> | <FILENAME> | <FORMAT> |

### D — Existing artefacts to reuse

| # | Artefact | Type | Where it lives | Why it is relevant |
|---|---|---|---|---|
| D1 | <NAME> | Automation \| API \| Connector \| Shared library \| Document model | <LOCATION> | <RELEVANCE> |

---

## Pre-sign-off checklist

- [ ] §1.2 states the KPI being moved; §1.3 criteria are numeric
- [ ] §2.3 out of scope is explicit, with reasons
- [ ] §5.3 every step has an actor; every decision has a stated decision nature
- [ ] §5.4 control-flow structure named concretely, or explicitly marked absent
- [ ] §5.5 stages, owners, SLAs at both levels, at-risk and breach behaviour, and every exit path
- [ ] §5.7 every human touchpoint has all outcomes named and a no-action behaviour
- [ ] §7 every rule numbered, testable, and — where possible — carrying a worked example
- [ ] Every threshold numeric, with its comparator, next to the role or action it gates
- [ ] §6.3 value mappings complete
- [ ] §8.1 exceptions numbered, with detection, action, and a catch-all row
- [ ] §8.4 irreversible steps flagged
- [ ] §9 per system: API or UI-only, cloud-reachable or on-prem, owner; inbound events have a correlation key
- [ ] §5.6 document storage location stated, not assumed
- [ ] §2.1 delivery model and product exclusions stated
- [ ] §13.1 one complete canonical case with concrete inputs and expected outputs
- [ ] §2.1 data sensitivity and no-log fields captured
- [ ] §11 reporting requirements captured
- [ ] Appendix A screenshots are readable raster images, annotated
- [ ] Every material fact traceable to a source in Authoritative References, or marked as an assumption
- [ ] No product/technology selection, prompts, selectors, schemas or connection details anywhere in this document
