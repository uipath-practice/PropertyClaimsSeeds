# Commands that fail while the thing they describe is fine

Each of these was met in a real build. In every case the command is wrong, not your solution — and each one
costs a diagnostic detour if you take it at face value.

## `--folder-key` takes a GUID, and a folder *name* fails silently

```bash
uip or processes list --folder-key ClaimCase-01     # looks fine. is not fine.
```

It does not error and does not return zero rows. It returns a **different, paginated, tenant-wide list** —
other seats' processes included — and `HasMore: true`. Every later conclusion drawn from it is wrong, and
nothing anywhere says so.

Pass the GUID. `--folder-path` is the flag that takes a name:

```bash
FK=$(uip or folders list --all --name ClaimCase-<NN> --output json --output-filter "[0].Key")
uip or processes list --folder-key "$FK" --output json
```

The general form is worth carrying: **any list that comes back bigger than you expected is scoped wrongly**, and
a list that comes back with `HasMore: true` has not answered your question at all.

## `uip solution deploy list` returns 403

```
Forbidden (403) — errorCode: "0004"
```

With or without `--folder-path`, and after a deploy that succeeded. Your account can deploy but not enumerate
deployments in this tenant.

**Instead:** `uip or processes list --folder-key <key>`. What landed is visible as processes.

## `uip maestro case process list` returns a generic error

```
Response returned an error code
```

**Instead:** `uip or processes list --folder-key <key>`, which returns the same processes including the case
itself, with the GUID you need to start it.

## `uip maestro case job status --detailed` and `case job traces` do not report

`job status --detailed` answers `unknown_error`; `job traces` starts streaming and then crashes with
`Cannot read properties of null (reading 'status')`.

**Instead**, and these two answer everything:

```bash
uip maestro case instance get       <instance-id> --folder-key <key>
uip maestro case instance incidents <instance-id> --folder-key <key>
```

## `uip or jobs start` wants the GUID, not the process key

`uip or jobs start ClaimCase-07.Case.ClaimLifecycle` fails with `HTTP 400: Undefined process`. The positional
argument is the `Key` GUID from `uip or processes list` — the dotted string is the `ProcessKey`, a different
field that looks more like an identifier and is not the one.

## `--folder-key` is accepted inconsistently

`uip or jobs list` takes it. `uip or jobs get` and `uip or jobs logs` reject it as an unknown option, and
`jobs logs` without it returns zero rows. `uip processes delete` rejects it while `processes create` requires it.

There is no rule to learn — check `--help` for the specific verb.

## `uip is connections get` does not exist

Use the `list` form in `known-issues/connections-list.md` and read the entry you want.

## The CLI's self-update reports a failure that does not matter

```
Update completed with failures — Unexpected npm pack output for @uipath/skills
```

It appears mid-command, repeatedly. The command you ran still completes and its result is valid. It is worth
logging once, then ignoring.
