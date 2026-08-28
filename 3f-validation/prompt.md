# Build — the Coded Action App

`PDD.md` §5.7 says what each of the two reviewers must be able to see, and it says **not a summary**. Build the **Coded Action App** they work in from Action Center — the one the Maestro case raises its `action` tasks against.

Use the **`uipath-coded-apps`** skill. The app already exists — created at `3d` **beside** the solution with its contract and an empty page, and deployed into your seat folder by its own command. This block replaces the empty page with the two screens and redeploys **the app alone** — `uip codedapp pack` → `publish -t Action` → `deploy --folder-key --client-id <the shared registration>` — the solution and the case untouched. The client id is what lets the screen read the Data Fabric record (`CONFIG.md`, *The Coded Action App signs in through a shared registration*); the app deployed at `3d` has none, because raising and completing tasks did not need it. Its lifecycle is separate on purpose (`CONFIG.md`, *Deploying*; Locked 67): a screen defect is fixed and redeployed in a minute, not a solution cycle. **`contracts/review-task.md` is the shape you implement** — the case already binds it, so it is not yours to change. It reads the Data Fabric entity and returns a decision.

**Four files carry the requirements, and nothing here repeats them.** What each reviewer must see, may change and decides — `PDD.md` §5.7 (the stages the claim is at, the checks with passes included, the settlement line by line, the three documents, two outcomes with a written reason). What the app hands back — `contracts/review-task.md`. Where each of those sits on the page — `3f-validation/layout.md`. How it looks — `3f-validation/brand.md`.

**The layout is decided; the styling is yours.** `3f-validation/layout.md` fixes the regions of both screens based on business user's requirements — header, where the claim is, the decision, the at-a-glance cards, the checks, the documents — with a wireframe and what each region must carry. `3f-validation/brand.md` carries the palette, type and CSS tokens — use these as official company style.

**Build it against payloads your own Agents actually produced**, not against payloads you imagined. Use claims from previous run to read what landed on the Data Fabric record.

Two gates handled by single app. First: Eligibility Check gate has five checks and no assessments. Second: Claim Review will have all payloads. 

**Done when** both `action` tasks render in Action Center with real content. Decision made in Action Center lands on the Data Fabric record and moves the case on. 
