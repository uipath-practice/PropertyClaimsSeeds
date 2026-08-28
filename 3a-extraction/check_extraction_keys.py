#!/usr/bin/env python3
"""Resolve every IXP path `sdd.md` reads against a real extraction payload.

The design reaches into the extracted claim with `=js:` expressions such as

    =js:(vars.claimDataJson?.ClaimIncident?.[0]?.TypeOfIncident?.Value || "")

and every one of them is optional-chained, so a **wrong key never throws** — the
binding silently yields "" or undefined and the failure surfaces stages later as
an Agent reasoning about a claim with no incident type. Measured 2026-08-27: a
design derived the keys from the taxonomy labels and got three of them wrong
(`TypeofIncident`, `DateofIncident`, `DateofSubmission`); nothing threw. This
script is how that is caught mechanically rather than by eye — run it at `3a`
against a payload from your own extraction, and again whenever a later block
adds a binding that reads the extraction.

    python3 3a-extraction/check_extraction_keys.py <payload.json> [more.json ...]

A payload file is the `out_ClaimIXPDataJSON` object of an `Extract Claim Data
(IXP)` job, saved as JSON:

    uip or jobs get <job-key> --output json | python3 -c \
      'import json,sys; print(json.dumps(json.loads(json.load(sys.stdin)["Data"]["OutputArguments"])["out_ClaimIXPDataJSON"]))' \
      > payload.json

Exit 0 when every path resolves on every payload, 1 otherwise.
"""

import json
import pathlib
import re
import sys

SDD = pathlib.Path(__file__).resolve().parent.parent / "sdd.md"

# vars.claimData?.ClaimClaimTotals?.[0]?.TotalClaimAmount?.Value?.Currency
# The `Json` is optional: `out_ClaimIXPDataJSON` is an OBJECT, so a design that follows
# contracts/claim-entity.md holds it in `claimData` and keeps `claimDataJson` for the
# stringified copy that lands in the column. Both names are read here — matching only
# `claimDataJson` reported "no paths found" on a correctly-named design (2026-08-28).
PATH = re.compile(r"vars\.claimData(?:Json)?((?:\?\.(?:\[\d+\]|[A-Za-z_][A-Za-z0-9_]*))+)")
STEP = re.compile(r"\?\.(\[(\d+)\]|([A-Za-z_][A-Za-z0-9_]*))")


def steps(tail):
    """The chain after `vars.claimData[Json]`, as ints (indexes) and strs (keys)."""
    return [int(m.group(2)) if m.group(2) is not None else m.group(3)
            for m in STEP.finditer(tail)]


def resolve(payload, chain):
    """Walk the chain the way optional chaining does: a miss is None, never a raise."""
    node = payload
    for step in chain:
        if isinstance(step, int):
            if not isinstance(node, list) or step >= len(node):
                return None, False
            node = node[step]
        else:
            if not isinstance(node, dict) or step not in node:
                return None, False
            node = node[step]
    return node, True


def paths_in_sdd():
    """Every distinct claimDataJson path in the design, with the lines that use it."""
    found = {}
    for n, line in enumerate(SDD.read_text(encoding="utf-8").split("\n"), 1):
        for m in PATH.finditer(line):
            found.setdefault(m.group(0), []).append(n)
    return found


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    found = paths_in_sdd()
    if not found:
        print(f"no vars.claimData / vars.claimDataJson paths found in {SDD} — has the design stopped reading the extraction?")
        return 1

    bad = 0
    for arg in sys.argv[1:]:
        payload = json.loads(pathlib.Path(arg).read_text(encoding="utf-8"))
        print(f"=== {arg} — {len(found)} distinct path(s) from sdd.md ===")
        for expr, lines in sorted(found.items()):
            chain = steps(PATH.fullmatch(expr).group(1))
            value, ok = resolve(payload, chain)
            where = ",".join(str(l) for l in lines)
            if not ok:
                bad += 1
                print(f"  MISSING  {expr}   (sdd.md:{where})")
            elif value in (None, "", {}, []):
                bad += 1
                print(f"  EMPTY    {expr} = {value!r}   (sdd.md:{where})")
            else:
                shown = value if not isinstance(value, (dict, list)) else json.dumps(value)
                shown = str(shown)
                print(f"  ok       {expr} = {shown[:60]}{'…' if len(shown) > 60 else ''}")
        print()

    groups = {"Claim", "ClaimClaimant", "ClaimProperty", "ClaimIncident",
              "ClaimDamageInventory", "ClaimClaimTotals"}
    for arg in sys.argv[1:]:
        payload = json.loads(pathlib.Path(arg).read_text(encoding="utf-8"))
        missing = groups - set(payload)
        rows = len(payload.get("ClaimDamageInventory") or [])
        print(f"{arg}: groups present {len(payload)}/6"
              + (f", MISSING {sorted(missing)}" if missing else "")
              + f", damage rows {rows}"
              + (" — a blob, not one row per item" if rows == 1 else ""))
        if missing or rows < 2:
            bad += 1

    print()
    print("every path resolves" if not bad else f"{bad} problem(s)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
