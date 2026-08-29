# Build — the seven Agents

**Seven agents, one per `PDD.md` §7 section — `contracts/components.md` names them and what each owns.** Nothing else is built here: the deterministic work is already deployed as the six provided RPA processes, or belongs in the Maestro Case as a connector activity or an expression.

Use the **`uipath-agents`** skill (low-code Agents). All seven inside your one solution — the Maestro case binds only Agents that live alongside it.

What each one must decide is `PDD.md` §7, by rule id. Do not re-derive it and do not soften it: those rules are what the Verify block tests.

Three things decide whether these are usable:

- **One concern, one owner.** An Agent may cite another Agent's finding as evidence; it may never re-raise it as its own. A reviewer sees every finding at once, so the same problem reported three times reads as three problems.
- **A finding must be visible to whatever reports it.** Before writing any check, ask whether that data actually reaches that component at that point — not whether it is on the document somewhere. An Agent asked to confirm something absent from its own input can only report it missing, confidently and wrongly.
- §7.9 says what to leave alone and which claim should settle by itself. Agents that only implement §7.1–§7.8 flag something on every claim.

**Done when:** 
- each one runs on a real claim and returns what §7 says it should, including on a claim with nothing wrong, where the right answer is that it found nothing
- solution is uploaded (`uip solution upload Build/ClaimCase-<seat> --force`), so all seven Agents open in Studio Web inside it. Everything you build is local until that upload.
