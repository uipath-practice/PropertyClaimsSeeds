# Build the Coded Action App

`PDD.md` §5.7 says what each of the two reviewers must be able to see. Build the **Coded Action App** the Maestro case raises its `action` tasks against in Action Center.

Use the **`uipath-coded-apps`** skill. The app already exists — created at `3d` **beside** the solution with its contract and an empty page, and deployed into your seat folder. This block replaces the empty page with the two screens and redeploys **the app alone** — `uip codedapp pack` → `publish -t Action` → `deploy --folder-key <seat folder> --client-id <the shared registration>` — the solution and the case untouched.

The client id for the app is what lets the screen read the Data Fabric record (`CONFIG.md`, *The Coded Action App signs in through a shared registration*); **`contracts/review-task.md` is the shape you implement**, the case already binds it, so don't change it. It reads the Data Fabric entity and returns a decision.

**Requirements:** 
- What each reviewer must see, may change and decides — `PDD.md` §5.7 (the stages the claim is at, the checks with passes included, the settlement line by line, the three documents, two outcomes with a written reason)
- What the app hands back — `contracts/review-task.md`. 
- Where each of those sits on the page — `3f-validation/layout.md`. Fixes the regions of both screens based on business user's requirements — header, where the claim is, the decision, the at-a-glance cards, the checks, the documents — with a wireframe and what each region must carry. **The layout is decided; the styling is yours.**
- How it looks — `3f-validation/brand.md`. Carries the palette, type and CSS tokens — use these as official company style.

**Build it against payloads your own Agents actually produced**, not against payloads you imagined. Use claims from previous run to read what landed on the Data Fabric record.

**Pause for a human before the first publish.** Serve the app locally on fixtures captured from your own records — development-only, never shipped — and ask your reviewer to open `http://127.0.0.1:<port>` with `?gate=eligibility`, `?gate=eligibility&state=decided`, `?gate=review`, `?gate=review&state=decided` — one screen state each, the decided review carrying a real settlement override. Apply what they find, then publish once.

**After the deploy, prove the write-back once per gateway without a browser**: raise a fresh claim, complete its task with `uip tasks complete`, read the record back — a task decided before a fix proves nothing (`contracts/review-task.md`). Validating the deployed screens inside Action Center is the reviewer's own optional check.

Two gates handled by single app. 
- First: **Eligibility Check** gate has five checks and no assessments. 
- Second: **Claim Review** will have all payloads. 

**Done when** 
- your reviewer has approved all four localhost states. 
- the app is republished alone and upgraded in place. 
- a fresh task per gateway, completed from the command line, lands its decision on the Data Fabric record and moves the case on. 
- a completed task still carries all its data when read back.
