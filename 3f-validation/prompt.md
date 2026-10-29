# The review screens

Build the two review screens in the **Coded Action App** the case raises its gate tasks against, with the **`uipath-coded-apps`** skill. The app already exists from the case block, with its contract and an empty page. Replace the page and redeploy **the app alone**; leave the solution and the case untouched.

Two gates, one app:
- **Eligibility check**: the five screening checks, no assessments yet.
- **Claim review**: everything the Agents produced.

Requirements:
- What each reviewer sees, may change and decides: `PDD.md` §5.7.
- What the app hands back: `contracts/review-task.md`. The case already binds it, so don't change it.
- Where each part sits on the page: `3f-validation/layout.md`. The layout is decided; the styling is yours.
- How it looks: `3f-validation/brand.md`, the company style.

Steps:
1. Leave a claim waiting at each gate, and build against what your own Agents wrote on those records, not against data you imagined.
2. **Pause for me before the first publish.** Serve the app locally on the records you captured and ask me to check four states: each gate open and decided, with a real settlement change on the decided review. Apply what I find.
3. Publish and deploy the app once.
4. Prove each gate writes back: a fresh claim per gate, its task completed from the command line, the decision read back from the record.
5. Leave one fresh claim waiting at each gate, so I can check the screens in Action Center.

**Done when:**
- I have approved all four local states
- the app is republished on its own and upgraded in place
- a fresh task per gate, completed from the command line, lands its decision on the record and moves the case on
- a completed task still shows all its data
- a claim waits at each gate for me.
