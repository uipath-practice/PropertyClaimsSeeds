# Known issues

Upstream defects you will meet, by **behaviour** — what you see and what to do instead. Read this before you debug anything, and before you believe an empty `list`: [`cli-commands.md`](cli-commands.md).

**A command exits 0, prints *"Checking for updates…"* and returns nothing** — the CLI updated itself and consumed the command. Run it again. **Exit 0 is not proof a command ran — check for the result you asked for.**

**On macOS the shell is zsh, which does not split an unquoted variable into words**: `for s in $SPECS` runs once with the whole string, and `cmd $ARGS` passes one argument. A pinned run that silently drops its `in_Discrepancy` comes back as a random claim — the answer key shows it. Use arrays, or `${=VAR}`.

**Before block 1, set up your machine**: a sandboxed agent shell, the local sign-in port and every Windows trap (JSON on a command line, BOMs, the cp1252 console) are in [`../CONFIG.md`](../CONFIG.md), *Your machine* and *Windows*.

**A command refused is one of three things, and each has its own fix.** Your agent's harness declined it (its message names a policy or an approval, and `uip` never ran): ask your operator. The CLI is not signed in: `uip login status` from your seat folder, and log in again only if it says so. The platform refused the resource (`403`, *Missing permissions*): the login is fine, a grant is missing, and it is your operator's.

**An entry here wrong, or fixed upstream?** Log it.
