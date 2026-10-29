# Verify

Every piece was checked as you built it. **Does the whole thing work?** `PDD.md` §13.2 lists the problems a real claim arrives with, and §1.3 says what success means in numbers.

Steps:
1. **Clean claims first.** Run six claims with nothing wrong, across different claimants. With fewer, one false escalation reads as a third of them against the PDD's one in ten.
2. **Then aim a claim at each planted problem**, in the same batch as the clean claims, and record what happened against both.
3. **Now read the answer key.** It sits with the claim documents and says what was planted and what should happen. Read it as what was put into the documents: a problem nothing plants is a false positive.
4. **Fix, redeploy, run the whole batch again**, with new clean claims each time. Three cycles, then run the batch you score and stop fixing.
5. **Check the build against the design**: every stage, task, rule, SLA and variable in `sdd.md`, marked implemented, missing, mismatch or extra. Look hardest at *extra*: nobody asked for it and no tool reports it.

What to establish:
- Each planted problem is caught by the Agent that owns it and stops the claim at the right gate. Not caught by something else, and not caught twice.
- A clean claim settles in full with no task ever raised, not even one whose checks are all green.
- The letter to the claimant matches what actually happened, including any concern a human ruled on.
- Two clean claims of the same claimant settle to the same cent.

Guidelines:
- Fix at the source, in the block that owns it, and fix everything a batch shows before you redeploy.
- A fix counts only on claims it was not tuned on. Over-flagging a clean claim is the failure that comes back, and closing one problem can open another.
- A run that finds nothing was probably not aimed.

**Done when** the batch you score ran after your last redeploy and shows:
- for each planted problem, which Agent caught it and which gate showed it to a person, or why it is still missed and the fix you would make next
- clean claims settled untouched, with at most one in ten referred to a person (`PDD.md` SC5), each referral named with its cause.
