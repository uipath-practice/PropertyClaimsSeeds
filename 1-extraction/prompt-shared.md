# Block 1b — use the shared extraction project

**Goal.** Point your build at the shared IXP project instead of training your own, and confirm it returns what
later blocks expect.

Take this route when time is short, or when your own project is not producing clean fields. **It is a supported
path, not a penalty** — the shared project is the same model, and every block after this one is identical.

**Read.** `1-extraction/spec.md` (the contract the extraction must satisfy) · `CONFIG.md` (the shared project's name)

**Do.**

1. Confirm you can see the shared project and that it has a live model version.
2. Generate one claim, run the form through the shared model, and read the output.
3. Record the project name and model version in your notes — later blocks bind to it, and your solution's
   documentation should say which extraction it used.

**Must hold.**

- The output carries all six field groups named exactly as `1-extraction/spec.md` lists them.
- A claim with several damage rows returns one `ClaimDamageInventory` occurrence per row.

**Done when.**

```bash
uip ixp projects list --output json                            # the shared project is visible
uip ixp projects list-models <project-name> --output json      # it has a version tagged live
```

Plus: one generated claim form extracts all six groups, with the right number of damage rows.

**Where it goes.** Generated code into `Build/ClaimCase<NN>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** Keep `build-findings.md` — including *why* you took this route. Whether people fall back, and
at what point, is one of the more useful things a build can tell us.
