#!/usr/bin/env python3
"""Record one workshop finding.

Writes a row to the shared WorkshopFindings table. That is the only place findings
live -- there is no local findings file to keep in step.

    python3 log-finding.py --block 5-case --category friction \
        --summary "uip maestro case validate passed but the deploy failed with ..."

Batch (a JSON array of {block, category, summary}):

    python3 log-finding.py --file my-findings.json

Everything else -- seat, agent, model, uip version, seed version -- is filled in for
you. If the insert fails the row is spooled to .workshop/spool.jsonl and retried on
the next call, so a finding is never lost to a network blip.
"""
import argparse, json, os, pathlib, re, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
STATE = HERE / ".workshop"
CACHE = STATE / "cache.json"
SPOOL = STATE / "spool.jsonl"
ENTITY = "WorkshopFindings"


def uip_exe():
    """`uip` on PATH is a shim, and on Windows Python cannot execute the bare name."""
    for name in ("uip", "uip.cmd", "uip.exe", "uip.bat", "uip.ps1"):
        found = shutil.which(name)
        if found:
            return found
    return "uip"


def uip(*args, timeout=180):
    """Run uip and return parsed JSON, or None. Never raises."""
    exe = uip_exe()
    cmd = [exe, *args, "--output", "json"]
    if exe.lower().endswith(".ps1"):
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", *cmd]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except Exception:
        return None
    m = re.search(r"^\s*\{", p.stdout, re.M)
    if not m:
        return None
    try:
        return json.loads(p.stdout[m.start():])
    except json.JSONDecodeError:
        return None


def cache():
    try:
        return json.loads(CACHE.read_text())
    except Exception:
        return {}


def save_cache(c):
    STATE.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(c, indent=1))


def entity_id(c):
    """The insert wants the entity id, not its name."""
    if c.get("entityId"):
        return c["entityId"]
    d = uip("df", "entities", "list", "--native-only") or {}
    for e in d.get("Data") or []:
        if e.get("Name") == ENTITY:
            c["entityId"] = e.get("Id")
            save_cache(c)
            return c["entityId"]
    return None


def seat(c):
    """Which seat this is -- answered locally, on purpose.

    The tenant is shared and every seat's folder lives on it, so asking
    Orchestrator returns whichever folder comes back first and stamps every
    finding with somebody else's seat. It did exactly that for a whole block on
    2026-08-20. This folder's name is the one answer that cannot be another
    seat's, so it wins over anything cached.
    """
    for d in (HERE, *HERE.parents):
        m = re.fullmatch(r"ClaimCase[-_](\d+)", d.name)
        if m:
            if c.get("seat") != m.group(1):
                c["seat"] = m.group(1)
                save_cache(c)
            return c["seat"]
    if c.get("seat"):
        return c["seat"]
    env = os.environ.get("WORKSHOP_SEAT", "").strip()
    if env:
        c["seat"] = env
        save_cache(c)
        return env
    # Last resort, and only when the tenant is unambiguous about it.
    d = uip("or", "folders", "list", "--all") or {}
    hits = {m.group(1) for f in (d.get("Data") or [])
            for m in [re.fullmatch(r"ClaimCase[-_](\d+)", (f.get("Name") or "").strip())] if m}
    if len(hits) == 1:
        c["seat"] = hits.pop()
        save_cache(c)
        return c["seat"]
    return "unknown"


def context(c, args):
    if not c.get("uipVersion"):
        try:
            out = subprocess.run([uip_exe(), "--version"], capture_output=True,
                                 text=True, timeout=120).stdout
            v = re.findall(r"\d+\.\d+\.\d+[\w.\-]*", out)
            c["uipVersion"] = v[-1] if v else "unknown"
        except Exception:
            c["uipVersion"] = "unknown"
        save_cache(c)
    seed = "unknown"
    try:
        # Both lines: the date alone cannot tell two seeds of the same day apart,
        # and the commit is what a finding has to be attributable to.
        seed = " ".join((HERE / "VERSION").read_text().split())
    except Exception:
        pass
    return {
        "seat": args.seat or seat(c),
        "codingAgent": args.agent or c.get("codingAgent") or os.environ.get("WORKSHOP_AGENT", "unknown"),
        "model": args.model or c.get("model") or os.environ.get("WORKSHOP_MODEL", "unknown"),
        "uipVersion": c["uipVersion"],
        "seedVersion": seed,
    }


def insert(eid, rows):
    """Insert via a temp file -- inline JSON does not survive PowerShell quoting."""
    STATE.mkdir(exist_ok=True)
    tmp = STATE / "insert.json"
    tmp.write_text(json.dumps(rows), encoding="utf-8")   # utf-8, no BOM
    d = uip("df", "records", "insert", eid, "--file", str(tmp))
    return bool(d and d.get("Result") == "Success"), (d or {}).get("Message", "no response")


def spool(rows):
    STATE.mkdir(exist_ok=True)
    with SPOOL.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def drain(eid):
    if not SPOOL.exists():
        return 0
    rows = [json.loads(l) for l in SPOOL.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not rows:
        return 0
    ok, _ = insert(eid, rows)
    if ok:
        SPOOL.unlink()
        return len(rows)
    return 0


def main():
    ap = argparse.ArgumentParser(description="Record a workshop finding.")
    ap.add_argument("--block", help="e.g. 5-case")
    ap.add_argument("--category", help="free text: friction, seed-gap, platform-bug, ...")
    ap.add_argument("--summary", help="what happened, what you tried, what happened next")
    ap.add_argument("--summary-file", help="read the summary from a file instead")
    ap.add_argument("--file", help="a JSON array of {block, category, summary}")
    ap.add_argument("--seat"); ap.add_argument("--agent"); ap.add_argument("--model")
    ap.add_argument("--identify", nargs=2, metavar=("AGENT", "MODEL"),
                    help="record who you are, once, for every later finding")
    ap.add_argument("--retry", "--flush", dest="retry", action="store_true",
                    help="send rows that failed earlier; adds nothing new, deletes nothing")
    a = ap.parse_args()

    c = cache()
    if a.identify:
        c["codingAgent"], c["model"] = a.identify
        if a.seat:
            c["seat"] = a.seat
        save_cache(c)
        # Echo the seat too: it is the half nobody checks, and a wrong one is
        # invisible until a whole block's findings turn out to be filed under
        # somebody else's number.
        print(f"identity recorded: seat {seat(c)} / {c['codingAgent']} / {c['model']}")
        return 0
    eid = entity_id(c)
    if not eid:
        print(f"! {ENTITY} not reachable -- check 'uip login status' and that you can see the\n"
              f"  tenant's entities. Findings are being spooled, not lost; run\n"
              f"  'python3 log-finding.py --retry' once it works.", file=sys.stderr)

    if a.retry:
        n = drain(eid) if eid else 0
        print(f"sent {n} finding(s) that were waiting")
        return 0

    if a.file:
        items = json.loads(pathlib.Path(a.file).read_text(encoding="utf-8-sig"))
    else:
        s = a.summary
        if a.summary_file:
            s = pathlib.Path(a.summary_file).read_text(encoding="utf-8-sig")
        if not (a.block and a.category and s):
            ap.error("need --block, --category and --summary (or --file)")
        items = [{"block": a.block, "category": a.category, "summary": s}]

    ctx = context(c, a)
    rows = [{**ctx, "processed": False,
             **{k: i[k] for k in ("block", "category", "summary") if k in i}}
            for i in items]

    if eid:
        drained = drain(eid)
        ok, msg = insert(eid, rows)
        if ok:
            extra = f" (plus {drained} recovered from the spool)" if drained else ""
            print(f"logged {len(rows)} finding(s) to {ENTITY}{extra}")
            return 0
        print(f"! insert failed ({msg}) -- spooled, will retry", file=sys.stderr)
    spool(rows)
    n = sum(1 for l in SPOOL.read_text(encoding="utf-8").splitlines() if l.strip())
    print(f"spooled {len(rows)} finding(s); {n} now waiting. "
          f"Run 'python3 log-finding.py --retry' before you finish the block.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
