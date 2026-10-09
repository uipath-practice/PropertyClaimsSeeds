# Agents — what bites

| Issue | Fix |
|---|---|
| A file-reading Agent has to be tested on a real file | Pass the **job-attachment object** a real job returned, whole, as the input — `{"ID": …, "FullName": "HO-41417123.pdf", "MimeType": "application/pdf", "Metadata": {}}` from `out_PolicyPDF` — and `uip agent debug` runs Analyze Files on the real PDF (`uipath-agents`, `debug.md`, *attachments*). Feed the file-less Agents a real prior output. The test is not waivable. |
| `agent debug` returns `OutClaimSummaryJSON` where the Agent emits `out_ClaimSummaryJSON` | `debug` PascalCases the output keys it prints. Bind the names in `agent.json`, never the ones `debug` shows. |
| A second `agent debug` fails with HTTP 500 | Two debug runs at once collide. Test Agents one at a time. |
| An Agent's output arrives downstream as broken JSON | Nothing enforces an Agent's output size; the case's slice guard cuts it mid-object. Check every output against its stated budget in the test, before the case consumes it (`contracts/claim-entity.md`, *Two budgets*). |
| A number is right once and wrong on the next run, or two fields of one envelope disagree | Run every Agent that computes a figure **at least three times on identical inputs** and assert the numbers match. In the same test, assert each figure against its other copies: claimed amounts against the form, the net against the envelope it is copied from, totals against the coverage lines. A difference is a defect, not noise; a single run hides it until a live claim pays the wrong amount. |
| An unreadable input ends the Agent in an error and faults the claim | An Agent always returns every field. A figure it cannot read is `-1`, a verdict it cannot reach is the escalating value, and either routes the claim to a human. Test each Agent once on a deliberately unreadable input. |
| Seven Agents fail the same way | They share a shape: prove one end to end on a real claim before building the other six. |
| A number is wrong and prompt revisions have not moved it | A low-code Agent writes its whole output in one call: **JSON key order is write order, and each key is committed before the next.** A verdict written first is one the reasoning then bends to fit. Order every envelope so a value that constrains another comes before it and a derived value after, at every level of nesting; put each derived scalar output right after the envelope it is copied from, and bind the case to the scalar. |
| One planted problem is reported twice, or missed while a neighbour flags something | A component ruled on a fact another owns — credibility on the claimed-to-assessed ratio (the settlement's check) or on the filing gap (screening's, already decided by a human) — or declined to rule on its own. Each Agent rules on its own §7 checks and **cites** the others' findings, never re-raises them. |
| A check now returns Fail and the claim still settles | Tell the decision Agent which failing checks are its own escalate or deny conditions — a failing peril classification **is** *coverage is disputed*. Re-run the aimed claim through the case after every detection fix. |
| Agents generated from one spec keep an old prompt | Shared text lives once in the spec and seven times on disk. After editing it, rebuild **every** Agent and re-run the proof; keep a check that diffs disk against spec. |
| A payload column holds invalid JSON on one claim in twenty | The form's blank fifth damage row: an Agent transcribing the schedule emits a trailing comma or an unclosed array on it. Tell it to skip empty rows, and parse every JSON output before you bind it. |
| Everything flags something on every claim | See below. This is the one that decides whether anything can ever settle. |

## Over-flagging is structural, not a wording problem

**Every clean claim comes back carrying a caution, and deleting the offending check moves it to the neighbouring one** — the behaviour is one caution per analysis, so wording alone never reaches a silent clean claim. Two things do:

- **Scope the escalation conditions** so a caution one analysis raises is not read as another's concern — a settlement warning is not *coverage is ambiguous*.
- **Write each §7.9 rule as its application, not as a quote.** `BR-73` quoted verbatim did not fire and a clean claim was denied on a corrosion exclusion; stated as the specific over-flag it exists to stop, the same claim approved.

A silent clean claim — nothing flagged anywhere, settled with no human — is reachable.

## An Agent whose verdict routes a claim reports facts; the case concludes

For each check that decides whether a claim reaches a human, have the Agent return the per-item facts the rule reads — one entry per statement, line or document fact, each with its finding (for credibility: `{quote, fitsClaimedCause}` per sentence of the claimant's account) — and write the conclusion as a case condition over those entries. The Agent still records its own verdict for the record and the screen; the route is the case's. A conclusion left to the prompt is the one that takes three verify cycles to hold.
