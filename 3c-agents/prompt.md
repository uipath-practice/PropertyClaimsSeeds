# The seven Agents

Build the seven Agents the PDD's analysis needs, one for each section of `PDD.md` §7, with the **`uipath-agents`** skill (low-code Agents). `contracts/components.md` names them and what each owns. Build all seven inside your one solution: the case binds only Agents that live beside it. Nothing else is built here; the deterministic work is already deployed or belongs in the case.

What each Agent decides is in §7, by rule id. Don't re-derive it and don't soften it: those rules are what Verify tests.

Steps:
1. Build one Agent and prove it end to end on a real claim before you build the other six.
2. Build the rest, and test each on real claims: one with a problem it owns, one with nothing wrong.
3. Test the Agents that compute figures for repeatability.
4. Upload the solution, so all seven open in Studio Web.

Guidelines:
- **One concern, one owner.** An Agent may cite another Agent's finding; it never re-raises it as its own. A reviewer who sees one problem reported three times reads three problems.
- **A check can only see its own input.** Before writing one, ask whether that data reaches this Agent at all. An Agent asked to confirm something it was never given reports it missing, confidently and wrongly.
- §7.9 says what to leave alone. Agents that only implement §7.1 to §7.8 flag something on every claim.

**Done when:**
- each Agent returns what §7 says on a real claim, including a claim with nothing wrong, where the right answer is that it found nothing
- every Agent that computes a figure returns the same figures on three runs of identical inputs, and each figure agrees with its own copies
- all seven open in Studio Web inside your solution.
