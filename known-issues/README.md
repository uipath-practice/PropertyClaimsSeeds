# Known issues

Upstream defects you will actually meet, described by **behaviour** — what you will see, and what to do instead. Read this before you debug anything, and before you believe a `list` that comes back empty.

No bug numbers are used as instructions. An entry keyed to a defect id becomes a lie the day the defect closes, and you would have no way to tell.

| File | Covers |
|---|---|
| [`cli-commands.md`](cli-commands.md) | commands that fail while the thing they describe is fine — folder keys, output filters, name matching |
| [`connections-list.md`](connections-list.md) | connection discovery returning a shape its siblings do not |

**Two that cut across everything**, and both cost a diagnostic detour if taken at face value:

**A command exits 0, prints *"Checking for updates…"* and returns no result.** The CLI updated itself and consumed your command in the process. Run it again; the second call works. **Exit code 0 is not proof a command ran — check for the result you asked for.**

**On Windows, JSON on a command line arrives mangled.** PowerShell rewrites quotes before the CLI sees them, so an argument that prints correctly is not the argument that was received, and the error names the JSON rather than the shell. Prefer `--file` wherever a command offers it, written UTF-8 **without a BOM**. Details in [`../CONFIG.md`](../CONFIG.md), *Windows*.

**Something here wrong, or fixed upstream?** Log it. An entry that has quietly become false is worse than a missing one.
