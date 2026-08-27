# Build — the validation app

`PDD.md` §5.7 says what each of the two reviewers must be able to see, and it says **not a summary**. Build the **Action App** they work in from Action Center — the one the case raises its `action` tasks against.

Use the **`uipath-coded-apps`** skill. **`contracts/review-task.md` is the shape you implement** — the case already binds it, so it is not yours to change. It reads the Data Fabric entity and returns a decision; it writes nothing else — `CONFIG.md` says why the registration it signs in through is read-only.

**Build it against payloads your own components actually produced**, not against payloads you imagined. Run a claim through first and read what landed on the record.

Two gates, one screen. What differs between them is what has happened by the time each opens: the first has five checks and no assessment at all, the second has everything. A screen that assumes the second will show a reviewer empty panels at the first and teach them the tool is broken.

**Done when** both `action` tasks render in Action Center with real content — waiting and decided — and a decision made there lands on the entity and moves the case on.
