# Build — the Process App

`PDD.md` §11 asks for the view the claims team lead has never had: every claim, where it is, how long it has been there, and what is waiting on a human. Build it as a standalone **Coded Web App** at `Build/property-claims-<seat>/` — beside the solution, published and deployed on its own into your seat folder, signed in through the shared registration (`CONFIG.md`, *The Coded Action App signs in through a shared registration* — the same client, the scopes it carries and no others).

Use the **`uipath-coded-apps`** skill — the web-app path, not the action-app path and not its dashboard generator. Read `6-process-app/layout.md` first: the three screens, and what the claim record and the case already carry. Decide the visuals yourself from that data.

**Re-use the Action App, do not rebuild it.** The claim screen is the one you built at `3f` — import it from `Build/claim-review-<seat>/src` (an alias into its source, so there is one claim view and two deployables) and take its stylesheet with it. Show its decision controls only while a gate task is open for that claim, and make completing them complete that Action Center task with `contracts/review-task.md`'s payload — outcome and outputs, the three identifiers replayed. The case then writes the record; the app never writes the claim record itself.

Never sum amounts across currencies (`PDD.md` A2). Read who decided from the gate conditions, not from the decision columns.

Before you build, write `6-process-app/design.md`: each screen, what it shows, from which column or call, and the map from your record's status words to the labels a handler reads. Ten lines a screen.

Build against your own records. Serve it locally, sign in, and reconcile the dashboard's counts with `uip df records list` before the first publish — a signed-in browser is your reviewer's; prove the arithmetic without one by running the app's own aggregation over the rows the CLI read. Then `npm run build` → `uip codedapp pack` → `uip codedapp publish` (a Web app, no `-t Action`) → `uip codedapp deploy --folder-key <your seat folder> --client-id <the shared registration>`.

**Done when:**
- the deployed app opens signed in from your seat folder, and its dashboard counts equal the record counts by status from the command line
- one search finds a claim by id, by policy number and by claimant name; the claim page renders a settled claim, a refused claim and one still in flight
- a claim with a pending task shows it; completing it from the app shows `Completed` in `uip tasks get <id>`, and the case writes the decision on the record and moves the claim on
