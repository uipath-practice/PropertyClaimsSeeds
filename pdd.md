# Property Claims — the process you are building

This describes a property insurance claims process end to end: who is involved, what happens in what order, what
each analysis decides, and where a human must sign off. Read it once in full before you build. It tells you *what*
must happen, not *which UiPath component* does it — deciding that, and wiring the data between the pieces, is the
work. Nothing here prescribes a payload shape, a variable name, or an agent prompt.

Document generation, retrieval and data extraction are **provided and already running** — you consume them.
Everything from eligibility screening onward is yours to build.

**Monetary limits, deductibles, sublimits, exclusions and the named-peril list are deliberately absent.** They live
in each claim's policy document, which is where your solution must read them from. A rule that hardcodes a limit
will be wrong on the next claim.

## 1. The claim

A homeowner suffers damage — fire, water, storm, theft — and claims against an **HO-3 homeowner's policy**. The
insurer must decide whether the claim is payable and for how much, then settle it or explain the refusal. Claims
arrive in several countries and currencies.

Each claim comes with exactly three documents:

| Document | Written by | Carries |
|---|---|---|
| **Claim submission form** | the claimant | Claimant and property details, policy number, incident date and type, a description of what happened, an itemised damage inventory with amounts, the total claimed, the submission date, whether temporary repairs were made |
| **Insurance policy** | the insurer | Policyholder, property address, effective and expiration dates, payment status, coverage sections and their limits, sublimits, the deductible, the exclusions list, the named perils, any endorsements |
| **Assessor report** | an independent assessor | Assessment date, assessor name and licence, observed damage, a professional **cause determination**, an independent repair estimate, the assessor's authorisation |

The three documents do not always agree. That is the point of the process, and §9 says what to expect.

**Only one of the three is a form.** The distinction decides how each document is read, and it is not a technical
detail — it is what these documents *are*:

| Document | Shape | So it is read by |
|---|---|---|
| Claim submission form | a **structured form**, same layout every time | document extraction, into a fixed set of fields |
| Insurance policy | **free prose** — coverage sections, exclusions, special conditions, endorsements, written differently by every insurer | an analysis, reading the document itself |
| Assessor report | **free prose** — written by an external contractor who may put anything in it, in any order | an analysis, reading the document itself |

Extraction suits the form and only the form. A policy's meaning lives in the wording of its clauses and an
analysis has to quote the exact sentence it relied on (§5.2) — flattening that into fields loses what the
decision rests on, and no fixed field set survives the next insurer's wording. The assessor's report, less
structured still, is the same.

**So the policy and the assessor's report reach the analyses as files.** Only the claim form is extracted.

## 2. Roles

| Role | Does |
|---|---|
| **Claimant** | Files the claim; is informed twice and receives a written decision |
| **Independent assessor** | Inspects the property and issues the assessor report |
| **Eligibility reviewer** | A human. Called in *before* an inspector is dispatched, and only when screening flagged something, to decide whether the claim proceeds — with a written reason |
| **Claims adjuster** | A human. Sees every analysis and makes the final call — with a written reason |
| **Analysis specialists** | Each examines exactly one aspect of the claim and reports what it found. None decides the claim |

**Only the two human roles decide anything.** An analysis reports; it can stop the process from advancing; it never
closes a claim on its own. §4 says where the one exception lies, and it runs in one direction only.

## 3. The lifecycle

Eight stages. **Five are primary — the main path — and three are secondary.** The split is what a case timeline
displays, so it is worth getting right, and the criterion is simple:

> **Primary is the path a healthy claim takes. Secondary is everything else** — a hold, an exception, and the
> unhappy ending.

Applied here that gives **primary**: intake, eligibility screening, analysis, claim review, approved. And
**secondary**: awaiting inspection (a hold — the claim waits on someone outside the process, and it is the one
stage a claim can return to), missing details (an exception), denied (the unhappy ending).

Making the *approved* ending secondary is the tempting mistake, because the two endings look symmetric. They are
not: approval is what a healthy claim does, and a portfolio view showing every settled claim as an exception is
one nobody can read.

**Intake.** Register the claim. Then **in parallel**: open the claim record and retrieve the documents. Then in
parallel again: retrieve the policy, look up prior claims against it, and tell the claimant the claim was received.

**Eligibility screening.** Run the five checks (§5.1) and record the result. **If any of the five failed, stop
for the eligibility reviewer**; if all five passed, the claim carries on with nobody looking at it. On both of
those routes the stage ends by requesting an assessor inspection — only a reviewer's refusal sends the claim
straight to the unhappy ending.

**Requesting the inspection is not a call the process makes.** The assessor is instructed outside this workflow;
what the process owns is the *waiting*. `Retrieve Inspection Report` returning not-ready is what "requested and
outstanding" looks like from inside the case — there is no dispatch process, and you should not build one.

**Awaiting inspection.** The claim waits until the assessor's report is ready, then moves to analysis. Give this
stage — and every stage — **no two ways in that can both be true at once**. Two entry conditions that can both
become true is a double execution waiting to happen. Mutually exclusive ones are fine, and one stage needs them:
*denied* is reached from the eligibility gateway and from claim review, and a claim takes exactly one of the two.

**Analysis.** Validate the assessor report first and turn it into structured data. Then, **in parallel**, three
independent analyses — coverage, payout, credibility — each reading the *structured* assessment rather than the
document: one reader, three consumers. Record what they found.

**Claim review.** Apply the decision rules (§5.6) for a recommended outcome, **record the recommendation**, then
**stop for the claims adjuster**, who sees every analysis side by side and decides. Record their decision.

The recommendation is deliberately made *here* rather than at the end of analysis: analysis establishes evidence,
review reaches judgement, and the reviewer needs the recommendation they are being asked to accept. **Record it
before the gateway opens** — the reviewer's screen is built from what has been written down, so a recommendation
written afterwards is one nobody can see (§8).

**Two endings, and a claim reaches exactly one.**

- **Approved** — draft the approval letter, then **in parallel** authorise the settlement and notify the claimant,
  then close the file.
- **Denied** — draft the refusal letter, then **in parallel** notify the claimant and record the denial.

They have the same shape on purpose: *write the letter → send it → record the outcome*. Approval carries the extra
money step. A claim denied at the eligibility gateway goes straight here, having had no analysis at all.

**Authorising the settlement means writing the approved amount to the claim record, and nothing else.** As with
the inspection, the outbound system is out of scope: the approved figure and who approved it are what this
process owes the next one, and paying it is that system's job.

**Missing details** — *a stage that waits, not a stage that works.* A real claim sometimes lacks a required
document: the claimant is asked for it and the claim waits. Build it as a placeholder — it must exist in the
lifecycle and must not do anything yet. Two structural facts, both easy to get wrong: **parallelism is expressed by grouping
work, not by ordering it** — sequencing three tasks does not make them concurrent. And **the two endings branch on
the *same* event** — claim review completing — with mutually exclusive tests, rather than one of them diverting the
claim out early. One event, two tests, nothing to race.

## 4. The two human decision points

| | Eligibility gateway | Final review |
|---|---|---|
| Placed | after eligibility screening, before an inspector is sent | after all four analyses |
| Opens when | one of the five screening checks failed | the analyses raise something worth a human |
| Answers | is this claim worth investigating? | is this claim payable, and for how much? |
| Sees | the five eligibility checks, the claim, the policy | every analysis, and the recommended outcome |
| Yields | continue or deny, plus the reviewer's reason | the final outcome, plus the adjuster's reason |
| Is | a **screening gate** — nothing about money has been decided | the **money decision** |
| Continue means | send for inspection | **approve the amounts and send for settlement** |
| Deny means | the claim closes immediately, with no assessment and no settlement | the claim closes after the full analysis |

Both must show the reviewer everything the analyses found, not a summary. The first exists to avoid paying for
an inspection on a claim that was never eligible, so the later analyses have not run when it opens — and on a
claim it denies they never will. What that means for the screen is `6-app/spec.md`'s to say.

**No claim is ever refused without a human.** An analysis that finds a fatal problem recommends denial and raises
it; the reviewer decides, and may override on compelling circumstances they can see and the documents cannot. So
**a failed screening check always opens the eligibility gateway** — that is the half of it that is never skipped.

**Approval is the direction that may run unattended, and it runs unattended at *both* gateways.** The point of
automating this at all is to clear the clean claims and spend human attention on the ones that need it, so:

- all five screening checks pass ⇒ **no eligibility reviewer**. The claim goes on to the inspection by itself.
- the analyses then raise nothing, and the payout is inside the §5.3 tolerance ⇒ **no adjuster**. The claim
  settles without a human seeing the amounts.

A spotless claim is therefore decided end to end by the process, with **no task raised at all**. That is the
intended outcome, not a hole in the controls: concerns still reach a human, they just reach the *right* one —
what screening can see stops the claim before an inspector is paid for, and what only the analyses can see stops
it at the final review with every finding on the screen.

Two rules make skipping safe, and they apply to both gateways equally:

- **Fail towards the human.** Skip only on an explicit "nothing to review". A missing or unreadable value means a
  reviewer looks at it. The test is `!== false`, never `=== true`.
- **Whatever runs after a gateway needs its own way to start**, or a skipped gateway leaves the claim waiting
  forever. This now applies to the step after screening too.

Everything downstream reads *the reviewer's decision if there was one, otherwise the recommendation* — write
that rule once and reuse it, or the two routes drift apart. And **write the automatic decision down as a
decision**: a claim that skipped a gateway still records what was decided and that no human decided it, or the
record shows a blank where the reviewer's answer would be, and nobody can tell a clean claim from a lost one.

## 5. What each analysis decides

**One concern, one owner.** Each analysis reports only on its own aspect. It may cite a fact another analysis
established as supporting evidence, but never as a finding of its own and never as the reason for its own result. A
reviewer sees every analysis at once, so one finding repeated three times reads as three unrelated problems.

**Nothing may depend on the claimant's signature.** The claim form is signed, but it reaches your solution as
extracted data and the extraction does not carry signature blocks — so an analysis asked to confirm one can only
ever report it missing, on a document that has it. An analysis that evaluates something it cannot possibly see
teaches a reviewer to discount caveats, which is the real damage. The assessor's report is different: it is read as
a document rather than as extracted fields, so its authorisation is visible and is in scope for §5.5.

### 5.1 Eligibility — five checks, and always all five

Report every one, passes included — a screen showing only failures reads as a broken form. A failure sets the
overall result; it does not stop the analysis.

1. **Policy status** — the policy is in force. Current or paid passes; lapsed, cancelled or expired fails.
2. **Identity** — claimant and policyholder are the same person. Allow nicknames, middle names and minor spelling
   differences; a genuinely different individual fails.
3. **Property address** — the claim form and the policy describe one physical address, after normalising
   formatting (`St.` / `Street`, `Apt` / `#`). Any real difference fails. **Only those two documents exist yet** —
   the inspection is requested *after* this screening, so there is no assessor report to compare against and its
   absence is not a finding. Checking the report against the claim and the policy is §5.5's job, once it exists.
4. **Coverage period** — the incident date falls within the policy's effective and expiration dates, inclusive.
5. **Filing deadline** — **60 calendar days** from incident to submission. Past that: a failure when the form offers
   no explanation, and *late with justification* — a caveat, not a failure — when it does.

### 5.2 Coverage — what the policy responds to

- **Dwelling and other structures are open-peril**: covered *unless* an exclusion applies. Every relevant exclusion
  in the policy must be walked and answered individually. "No exclusions apply" is not an analysis.
- **Personal property is named-peril**: the loss must match one of the perils the policy names, or it is not covered.
- **Loss of use** follows the underlying peril — covered if that peril is, excluded if it is not.
- **Special conditions** — a property vacant more than **60 consecutive days** before the loss brings extra
  exclusions and a **15% reduction**; whether the claimant acted to limit further damage; any sign of other insurance.
- Assign **every** damage item to a coverage section and mark it covered or excluded.

Where the claim form's incident type conflicts with the assessor's cause determination, **the assessor's
determination governs the coverage analysis**, and the conflict is recorded.

**Two ways to be wrong about a policy.** Both were seen on real claims, and both make an analysis look careful
while it is not:

- **An exclusion's heading is a label; the exclusion is the sentence under it.** A heading reading *Water Damage*
  above text excluding seepage *"over a period of 14 or more days"* excludes long-term seepage and nothing else. A
  burst pipe that flooded a flat in an afternoon is covered. Whenever you exclude something, quote the words you
  relied on — if they do not fit the facts, the exclusion does not apply.
- **A condition nobody wrote down is not engaged.** Whether a property was vacant, who occupied it, how long it
  stood empty — these matter to the policy and appear in the paperwork only when someone recorded them. Where the
  documents are silent, say the condition does not apply and move on. Asking a reviewer to confirm four things
  nobody ever recorded is how they learn to stop reading the caveats.

### 5.3 Payout — the arithmetic, and nothing else

**Payout computes; it does not adjudicate coverage.** To produce a settlement it has to assign every damage item
to a coverage section and mark it covered or excluded — that is unavoidable arithmetic, not a second opinion. What
it must never do is raise a *finding* about coverage: whether the policy responds to this peril is the coverage
analysis's question, and a reviewer who sees the same concern from two analyses reads it as two problems. The two
run independently and neither waits for the other.

**Every row starts at the amount claimed.** A covered item pays the claimed amount or its cap, whichever is lower;
an excluded item pays nothing. **The assessor's estimate is evidence, not a ceiling** — the only thing that reduces
a claim without a human deciding is the policy cap, because that is the contract. Settling quietly at the assessor's
lower figure makes "pay less than was asked" the default outcome and leaves no trace that anything was decided.

1. Total the covered items per coverage section, then cap each section at its policy limit.
2. Cap the sublimited personal-property categories (jewellery, watches and precious items; electronics; anything
   else the policy schedules), then re-total that section.
3. **Cap at whatever the policy's annual aggregate has left.** The policy states a maximum payable for all
   property losses in one policy period, and the prior-claims lookup returns what earlier settled claims in that
   period have already paid out. Subtract one from the other; where the covered total exceeds the remainder, reduce
   the rows and say which limit bound them. **No prior claims is a result, not missing data.**
4. **Subtract the deductible once, from dwelling + other structures + personal property combined.** It does **not**
   apply to loss of use. If that combined total is below the deductible those coverages pay nothing — a valid covered
   claim that happens to pay zero, **not** a denial.
5. Settlement basis: replacement cost where the policy's endorsement is active, otherwise actual cash value. With no
   depreciation data, present replacement cost and flag the adjustment as outstanding.
6. Net payout = the capped sections, less the deductible, plus loss of use **after its own limit**.
7. **Reasonableness** — compare the claimed **total** against the assessor's independent **total**. More than
   **20%** above it is flagged. Compare totals, never single items: two independent estimates of the same damage
   always differ line by line, and treating that as a finding buries the claims that deserve one.

**Never convert a currency.** Report in the currency of the claim.

**The aggregate is the one cap a claimant cannot check for themselves.** Every other reduction is printed on a
document they hold. This one rests on a claim history only the insurer has, so it always goes to a human before
the money is set, and the reason names the earlier claim and what it consumed — a correct settlement the
claimant cannot verify becomes a complaint.

### 5.4 Credibility — four behavioural reads, each low, medium or high risk

- **Narrative consistency** — does the claimant's account match the assessor's findings? Material contradictions
  only; differences in wording are expected.
- **Estimate behaviour** — the claimed-to-assessed **ratio**, never an amount, and read as behaviour: at or below
  **1.20** two professionals are agreeing; above it, the pattern is worth noting alongside the other three reads.
  **Credibility never flags the gap itself.** That is the same test §5.3.7 gives to payout, at the same threshold,
  and §5 forbids one fact reaching a reviewer as two problems — so payout owns the finding and credibility may
  only cite it.
- **Documentation completeness** — the assessor's licence number, itemised descriptions rather than bare
  amounts. Missing paperwork is not fraud; it may mean the claim is not ready to adjudicate. **A field that is
  legitimately empty is not missing** — not every country has a state or province.
- **Timing and pattern** — a submission gap beyond 30 days is notable and beyond 45 a flag; an assessment on the day
  of the incident, or more than 60 days after it, is notable; prior claims are read for frequency and similarity.

Credibility reads timing as **behaviour**. The contractual deadline test belongs to eligibility, and only there —
and by the same rule the amount comparison belongs to payout, and only there.

### 5.5 Assessor report validation — the gate before the parallel analyses

Confirm the document is the assessor report for *this* claim; that it carries assessor name, licence, assessment
date, property, incident date, cause determination, damage observations, estimate and authorisation; that its
details match the claim and the policy; and that it does not contradict itself. Produce the structured assessment
the three parallel analyses read, and conclude with one of: proceed, escalate, or unusable.

### 5.6 The decision rules — applied in this order

These produce a **recommendation**, not an outcome. Nothing here closes a claim.

1. **Recommend denial** if eligibility failed on the policy, the identity, the address, or the coverage period
   without justification; or coverage is none and nothing is flagged for escalation; or the payout is zero
   *because every item is excluded*. A payout absorbed by the deductible is not a denial.
2. **Escalate** if the filing was late but justified; coverage is ambiguous or disputed; the claim exceeds the
   independent estimate by more than 20%; credibility is high risk; the net payout exceeds 20% of the dwelling
   limit; or the annual aggregate bound the settlement.
3. **Partial approve** where some items are covered and some excluded.
4. **Approve** otherwise.
5. **Confidence** — no flags is high, one is medium, two or more is low.

List *every* reason that applies, not the first one found. Recommending approval for a claim that also meets an
escalation condition is a contradiction, not a judgement call — **escalation wins**. Priority whenever two apply:
**deny, then escalate, then partial approve, then approve.**

## 6. What a human approval binds

A reviewer at a gateway does not merely let the claim past — they **accept its exceptions**. A late notice they
approved is a *granted exception*, not an outstanding breach. So every stage after a gateway receives three things,
not one: the findings, **the decision**, and **the reviewer's written reason** — and reads them this way:

> A finding the reviewer saw and approved is settled. Record it as context where it bears on your own analysis and
> cite their reason, but never restore it to a failure or a warning on your own authority. Where the reviewer's note
> contradicts a finding, the note wins — they had the documents and the discretion. Only a fact **you** discovered
> yourself justifies raising a concern.

Get this wrong and the reviewer is asked the same question twice, the audit trail says the claim failed after it was
approved, and a human's *yes* becomes a machine's *no*.

**A skipped gateway binds nothing, and that is not the same as a reviewer who said nothing.** Nothing was
accepted because nothing was raised. Hand the later stages an explicit "no human has spoken" rather than a blank
reason, or they will read the blank as approval of everything.

## 7. Keeping the claimant informed

**Twice.** Claim received, at intake — and the outcome, from whichever ending the claim reaches. The mid-process
"still working on it" notices were removed: they told the claimant nothing they could act on.

The outcome message carries the **decision letter** itself, so the letter is written *before* the message is sent,
inside the same ending — which is also why each ending drafts its own rather than one being drafted before the
branch: a claim denied at the eligibility gateway never passes through review, and would be notified with
nothing to send.

The letter explains; it never analyses. Two letters exist and there is no third — **never write to a claimant that
their claim is still under review.** By the time a letter is drafted the claim has an ending, and the analyses that
raised concerns were ruled on before it. Explain the outcome using them; never re-open their questions, and never
ask an approved claimant for a document the decision did not depend on.

## 8. The claim record, and why every step writes to it

There is one record per claim, and it is the only thing that outlives a step. Each stage writes what it produced —
the extracted claim, each analysis, the recommendation, each decision, the letter, the outcome. Three consequences
shape the whole build, and each of them cost us a working day to learn:

- **A human step can only show what has already been written.** The reviewer's screen is built from the record, not
  from whatever is in flight. So an analysis a reviewer must see has to be **recorded before their step opens** —
  recording it afterwards produces a screen that says *not available yet* while the case runs perfectly.
- **Write nothing rather than write blank.** Sending an empty value where a step produced none **erases what an
  earlier step wrote**; omitting the field leaves it intact. Every optional field needs the "no value" case
  handled deliberately, or a later stage quietly destroys an earlier stage's work.
- **A completed human step keeps only what it was given plus what it returned.** Anything it needs in order to be
  re-opened later — above all the claim's identifier — must be part of that, or a decided review can never be
  read again.

## 9. What the documents will throw at you

Claims arrive with problems deliberately planted in them, at most one screening-level and one review-level per
claim. **Catching these is how you will know the solution works** — so each row below names what to look for, which
analysis owns it, and what it must produce. An analysis that misses its row is not a style difference. Note what
the right-hand column does *not* say: none of these closes a claim. The analysis fails its check and says why,
and a human decides what that is worth (§4).

### Screening — from the claim form and the policy alone

At this point those are the only two documents in existence. The inspection has not been requested yet, so there is
no assessor report to compare against and its absence is not a finding.

| Look for | Owner | What must happen |
|---|---|---|
| Premium unpaid from a date before the loss — the schedule still shows every limit, only the payment status gives it away | eligibility, policy status | **Policy status fails**, saying the policy was not in force on the day of loss. Recommends denial. |
| The named insured is a **different person** from the claimant. Same surname and same address is common; a different given name is a different individual | eligibility, identity match | **Identity fails**, naming who the policy is in. A reviewer may grant the exception once a relationship is documented. |
| The policy address differs from the claim address by a transposed unit or house number, with street, city and postcode all agreeing | eligibility, address match | **Address fails**, quoting both addresses. |
| The policy term ended days before the loss and was never renewed — payment status stays truthful | eligibility, coverage period | **Coverage period fails**, giving the loss date and the policy period. |
| The loss happened more than **60 days** before the claim was filed | eligibility, filing deadline | **Filing deadline fails** with no explanation on the form; a caveat rather than a failure where the form explains the delay. |

**Two of these are designed to slip past a careless reading.** The identity check is told that nicknames and minor
spellings are *acceptable*, so an analysis matching on how similar two strings look waves a spouse's policy
through. The address check is told to normalise `St.`/`Street` and `Apt`/`#` — which will not close a one-digit
gap, because everything except the number still matches.

### Review — needs the assessor's report, or the claim history

| Look for | Owner | What must happen |
|---|---|---|
| Every figure on the claim sits 25–40% above the assessor's independent estimate | payout, reasonableness | **Flagged**, quoting both totals. Never quietly settle at the lower one. |
| The incident type on the form is not the cause the assessor determined | coverage, peril classification | **Flagged.** The assessor's determination governs the coverage analysis; record the discrepancy. |
| The claimant's own account asserts something that rules out the cause they are claiming | credibility, narrative consistency | **Flagged.** Quote the two statements side by side. |
| An earlier settled claim in the same policy period has consumed most of the annual aggregate | payout, aggregate limit | **Reduce and flag.** Cap the settlement at what remains and name the earlier claim. |

The last two are the hard ones, for opposite reasons. The narrative contradiction has **nothing missing and
nothing malformed** — every document is internally fine, and it is visible only to something that reads both
accounts and understands them. The aggregate erosion is not in the documents **at all**: the claim is clean, the
peril is covered, the assessor agrees, and the settlement still comes out below the amount asked for.

### And sometimes nothing is wrong

Roughly a third of claims carry no planted problem at all. Those must pass every screening check and then
**settle in full with no human touching them at any point** — both gateways skipped, no task ever raised. A
solution that finds something to flag on every claim has not passed; it has just learned to always say yes to the
question *"is anything wrong here?"*, and it can never auto-settle anything. **A clean claim raising no task is
the pass, not a silence** — the first time you run one it looks as though the case did nothing, because the
screen you were waiting to answer never appears. Read the record and the timeline instead: the checks, the
analyses and the letter are all on it, and the ending is *approved*. The corollary matters when you demo: **to
see the reviewer's screen at all you have to aim the run at it.**
