# Known issues

Upstream defects you will meet, by **behaviour** — what you see and what to do instead. Read this before you debug anything, and before you believe an empty `list`: [`cli-commands.md`](cli-commands.md).

**A command exits 0, prints *"Checking for updates…"* and returns nothing** — the CLI updated itself and consumed the command. Run it again. **Exit 0 is not proof a command ran — check for the result you asked for.**

**On macOS the shell is zsh, which does not split an unquoted variable into words**: `for s in $SPECS` runs once with the whole string, and `cmd $ARGS` passes one argument. A pinned run that silently drops its `in_Discrepancy` comes back as a random claim — the answer key shows it. Use arrays, or `${=VAR}`.

**On Windows**, JSON on a command line arrives mangled — [`../CONFIG.md`](../CONFIG.md), *Windows*.

**An entry here wrong, or fixed upstream?** Log it.
