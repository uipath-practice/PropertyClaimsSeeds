# The process app

`PDD.md` §11 asks for the view the claims team lead has never had: every claim, where it is, how long it has been there, and what is waiting on a person. Build it as a standalone **Coded Web App** with the **`uipath-coded-apps`** skill (the web-app path), beside the solution, deployed on its own to your seat folder and signed in through the shared registration in `CONFIG.md`.

Read `6-process-app/layout.md` first: the three screens, and what the claim record and the case already carry. The visuals are yours.

Steps:
1. **Write a short design first**, in the block's folder: each screen, what it shows and where the data comes from, and how the record's status words become labels a claims handler reads.
2. **Re-use the claim screen from the review app; don't rebuild it.** One claim view, two apps. Show its decision controls only while a gate task is open for that claim, and let them complete that task. The case writes the record; this app never does.
3. **Build against your own records.** Serve it locally and prove the dashboard's counts match the records before the first publish.
4. Publish and deploy the app.

Guidelines:
- Never add up amounts in different currencies (`PDD.md` A2).
- Who decided comes from the gate, not from the decision columns.

**Done when:**
- the deployed app opens signed in, and the dashboard's counts equal the record counts by status
- one search finds a claim by id, by policy number and by claimant name; the claim page shows a settled claim, a refused one and one still in flight
- a claim with a pending task shows it, and completing it in the app completes the Action Center task and moves the claim on.
