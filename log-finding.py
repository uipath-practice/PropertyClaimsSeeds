#!/usr/bin/env python3
"""Record one workshop finding.

Writes a row to the shared WorkshopFindings table. That is the only place findings
live -- there is no local findings file to keep in step.

    python3 log-finding.py --block 5-case --category friction \
        --summary "uip maestro case validate passed but the deploy failed with ..."

Findings are not only complaints. Four optional fields turn one into a recommendation:

    --source    where the answer actually came from -- seed | skill | cli-help |
                docs | model | trial-error
    --ask       what should change here -- keep | cut | fix | add | move | none
    --artifact  which seed file and section, e.g. 5-case/cookbook.md#Wiring an action task
    --evidence  the exact error, the command, or the few lines that show it

Batch (a JSON array of {block, category, summary, ...}):

    python3 log-finding.py --file my-findings.json

Everything else -- seat, agent, model, effort, OS and shell, uip and skills
versions, seed version -- is filled in for you. A row that cannot be sent is spooled
to .workshop/spool.jsonl and retried on the next call.

    python3 log-finding.py --retry

sends whatever is waiting and then asks the table how many rows it holds for this
seat. Run it at the end of every block. **It exits non-zero while anything is still
unsent** -- so does a failed log -- because the one thing this script must never do
is report a finding as recorded when it is not.
"""
import argparse, json, os, pathlib, platform, re, shutil, subprocess, sys

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
    """The insert wants the entity id, not its name.

    We also remember each column's name and its length limit. The table gains
    columns over time and a seat may be running an older seed, so the row is
    filtered to what the table actually has before it is sent -- an unknown column
    fails the whole insert, taking the findings with it. The limits are read for the
    same reason: a value one character over its column's limit is refused, and the
    refusal takes the rest of the batch with it.
    """
    if c.get("entityId") and c.get("entityLimits"):
        return c["entityId"]
    d = uip("df", "entities", "list", "--native-only") or {}
    for e in d.get("Data") or []:
        if e.get("Name") == ENTITY:
            c["entityId"] = e.get("Id")
            c["entityLimits"] = {f["Name"]: (f.get("FieldDataType") or {}).get("LengthLimit") or 0
                                 for f in (e.get("Fields") or []) if f.get("Name")}
            c["entityFields"] = list(c["entityLimits"])
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
        m = re.fullmatch(r"ClaimCase[-_]([A-Za-z0-9]{1,12})", d.name)
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
            for m in [re.fullmatch(r"ClaimCase[-_]([A-Za-z0-9]{1,12})", (f.get("Name") or "").strip())] if m}
    if len(hits) == 1:
        c["seat"] = hits.pop()
        save_cache(c)
        return c["seat"]
    return "unknown"


def skills_version():
    """The uipath-* skills ship as one versioned bundle; that number is what tells
    us, later, whether a cookbook line went redundant because the skills improved."""
    for base in (pathlib.Path.home() / ".uipath" / ".skills",):
        try:
            return json.loads((base / "package.json").read_text()).get("version") or "unknown"
        except Exception:
            pass
    d = uip("skills", "list") or {}
    store = ((d.get("Data") or {}).get("StorePath") or "").strip()
    if store:
        try:
            return json.loads((pathlib.Path(store) / "package.json").read_text()).get("version") or "unknown"
        except Exception:
            pass
    return "unknown"


def os_stamp():
    """Shell as well as OS: PowerShell quoting alone has cost two seats a morning."""
    shell = os.environ.get("SHELL") or os.environ.get("ComSpec") or ""
    if os.environ.get("PSModulePath"):
        shell = "powershell"
    return f"{platform.system()} {platform.release()} / {pathlib.Path(shell).name or 'unknown'}"[:200]


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
    if not c.get("skillsVersion"):
        c["skillsVersion"] = skills_version()
        save_cache(c)
    return {
        "seat": args.seat or seat(c),
        "codingAgent": args.agent or c.get("codingAgent") or os.environ.get("WORKSHOP_AGENT", "unknown"),
        "model": args.model or c.get("model") or os.environ.get("WORKSHOP_MODEL", "unknown"),
        "effort": args.effort or c.get("effort") or os.environ.get("WORKSHOP_EFFORT", "unknown"),
        "uipVersion": c["uipVersion"],
        "skillsVersion": c["skillsVersion"],
        "osShell": os_stamp(),
        "seedVersion": seed,
    }


TRIM = " [trimmed]"


def fit(rows, limits):
    """Trim a value to its column's limit instead of losing the batch.

    Data Fabric refuses the row, not the field, so one over-long value takes its
    neighbours down with it. A visibly trimmed finding is worth more than a lost
    one, and the note says which -- nobody should read a cut-off error as the
    whole error.
    """
    if not limits:
        return rows
    out, trimmed = [], []
    for r in rows:
        row = {}
        for f, v in r.items():
            lim = limits.get(f) or 0
            if isinstance(v, str) and lim and len(v) > lim:
                row[f] = v[:max(0, lim - len(TRIM))] + TRIM
                trimmed.append(f"{f} ({len(v)} chars into a {lim}-char column)")
            else:
                row[f] = v
        out.append(row)
    if trimmed:
        print("note: trimmed to fit " + "; ".join(sorted(set(trimmed))), file=sys.stderr)
    return out


def insert(eid, rows, known=None, limits=None):
    """Insert via a temp file -- inline JSON does not survive PowerShell quoting.

    Returns (sent, failed), where failed is a list of (row, why).

    **A batch is not all-or-nothing, and the envelope hides it.** One bad row in a
    batch returns `Result: Success` with `FailureCount: 1`, so a caller that checks
    Result alone reads a partly-failed send as a clean one and drops the rows that
    never landed. That is exactly how seven findings were lost on 2026-08-21. The
    per-row verdicts are in Data.FailureRecords, each with its own Error naming the
    cause -- and on a whole-batch refusal the cause is in Instructions, not in the
    generic Message.

    Filtered to the table's real columns at send time rather than at write time,
    so a row spooled before a column existed still lands afterwards.
    """
    STATE.mkdir(exist_ok=True)
    if known:
        k = set(known)
        dropped = sorted({f for r in rows for f, v in r.items() if f not in k and v not in (None, "")})
        if dropped:
            print(f"note: this table has no column for {', '.join(dropped)} yet — "
                  f"those values were not sent. Everything else was.", file=sys.stderr)
        rows = [{f: v for f, v in r.items() if f in k} for r in rows]
    rows = fit(rows, limits)
    tmp = STATE / "insert.json"
    tmp.write_text(json.dumps(rows), encoding="utf-8")   # utf-8, no BOM
    d = uip("df", "records", "insert", eid, "--file", str(tmp))
    if not d:
        # No parseable answer means we do not know whether the rows landed. They
        # are spooled, because a duplicate is recoverable and a loss is not --
        # but say which it is rather than reporting a clean failure.
        return [], [(r, "no answer from uip -- these may or may not have landed; "
                        "a retry can duplicate them") for r in rows]
    if d.get("Result") != "Success":
        why = d.get("Instructions") or d.get("Message") or "the insert was refused"
        return [], [(r, why) for r in rows]
    bad = (d.get("Data") or {}).get("FailureRecords") or []
    if not bad:
        return rows, []
    # Match each rejected row back to what we sent. The echo comes back
    # PascalCased, so lower the first letter before comparing.
    pool, failed = list(rows), []
    for b in bad:
        echo = {f[:1].lower() + f[1:]: v for f, v in (b.get("Record") or {}).items()}
        hit = next((r for r in pool if all(r.get(f) == v for f, v in echo.items() if f in r)), None)
        if hit is None:                                  # fall back to the summary alone
            hit = next((r for r in pool if r.get("summary") == echo.get("summary")), None)
        if hit is not None:
            pool.remove(hit)
        failed.append((hit if hit is not None else echo,
                       b.get("Error") or "rejected without a reason"))
    return pool, failed


def why_lines(failed):
    """One line per distinct reason -- the same limit hit by six rows is one fact."""
    return sorted({w for _, w in failed})


def spool(rows):
    STATE.mkdir(exist_ok=True)
    with SPOOL.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def drain(eid):
    """Send the spool, claiming it first so two processes cannot send it twice.

    Returns (sent, failed) -- and `failed` is the half that matters, because a
    retry that could not send is not the same event as a spool that was empty.

    Read-insert-then-delete looks fine and is not: two of these running at once
    both read the same rows, both insert them, and the table gets a duplicate of
    every one -- which is worse than a lost row in a table whose whole purpose is
    counting how often a friction recurs. It happened on 2026-08-20 (findings 74).
    An atomic rename is the claim: exactly one process can win it, and if the
    insert then fails the rows are renamed back rather than dropped.
    """
    if not SPOOL.exists():
        return 0, []
    claim = SPOOL.with_suffix(".sending.%d" % os.getpid())
    try:
        SPOOL.rename(claim)           # atomic; the loser gets FileNotFoundError
    except OSError:
        return 0, []
    rows = [json.loads(l) for l in claim.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not rows:
        claim.unlink()
        return 0, []
    c = cache()
    sent, failed = insert(eid, rows, c.get("entityFields"), c.get("entityLimits"))
    if failed:
        # Only what failed goes back -- re-spooling the whole claim would send the
        # rows that did land a second time, and a duplicate is as bad as a loss in
        # a table whose purpose is counting how often a friction recurs.
        with open(SPOOL, "a", encoding="utf-8") as f:
            for r, _ in failed:
                f.write(json.dumps(r) + "\n")
    claim.unlink()
    return len(sent), failed


def waiting():
    """How many rows are still in the spool."""
    try:
        return sum(1 for l in SPOOL.read_text(encoding="utf-8").splitlines() if l.strip())
    except Exception:
        return 0


def table_count(eid, s):
    """How many findings the table actually holds for this seat.

    "The insert reported success" and "the row is in the table" are two different
    claims, and on 2026-08-21 they disagreed for seven findings across one block.
    This is the second claim, and it is the one worth making.
    """
    STATE.mkdir(exist_ok=True)
    tmp = STATE / "query.json"
    tmp.write_text(json.dumps({"filterGroup": {"logicalOperator": 0, "queryFilters": [
        {"fieldName": "seat", "operator": "=", "value": s}]}}), encoding="utf-8")
    d = uip("df", "records", "query", eid, "--file", str(tmp), "--limit", "1")
    if not d or d.get("Result") != "Success":
        return None
    return (d.get("Data") or {}).get("TotalCount")


def main():
    ap = argparse.ArgumentParser(description="Record a workshop finding.")
    ap.add_argument("--block", help="e.g. 5-case")
    ap.add_argument("--category", help="free text: friction, seed-gap, platform-bug, ...")
    ap.add_argument("--summary", help="what happened, what you tried, what happened next")
    ap.add_argument("--summary-file", help="read the summary from a file instead")
    ap.add_argument("--file", help="a JSON array of {block, category, summary}")
    ap.add_argument("--source", help="where the answer came from: seed | skill | cli-help | docs | model | trial-error")
    ap.add_argument("--ask", help="what should change in the seed: keep | cut | fix | add | move | none")
    ap.add_argument("--artifact", help="which seed file and section, e.g. 5-case/cookbook.md#Wiring an action task")
    ap.add_argument("--evidence", help="the exact error, the command, or the few lines that show it")
    ap.add_argument("--evidence-file", help="read the evidence from a file instead")
    ap.add_argument("--seat"); ap.add_argument("--agent"); ap.add_argument("--model")
    ap.add_argument("--effort", help="the reasoning/effort tier you are running at, e.g. medium, high")
    ap.add_argument("--identify", nargs=2, metavar=("AGENT", "MODEL"),
                    help="record who you are, once, for every later finding")
    ap.add_argument("--retry", "--flush", dest="retry", action="store_true",
                    help="send what failed earlier, then report what the table holds; "
                         "adds nothing new, deletes nothing")
    a = ap.parse_args()

    c = cache()
    if a.identify:
        c["codingAgent"], c["model"] = a.identify
        if a.seat:
            c["seat"] = a.seat
        if a.effort:
            c["effort"] = a.effort
        save_cache(c)
        # Echo the seat too: it is the half nobody checks, and a wrong one is
        # invisible until a whole block's findings turn out to be filed under
        # somebody else's number.
        print(f"identity recorded: seat {seat(c)} / {c['codingAgent']} / {c['model']}"
              f" / effort {c.get('effort', 'unknown')}")
        return 0
    eid = entity_id(c)
    if not eid:
        print(f"! {ENTITY} not reachable -- check 'uip login status' and that you can see the\n"
              f"  tenant's entities. Findings are being spooled, not lost; run\n"
              f"  'python3 log-finding.py --retry' once it works.", file=sys.stderr)

    if a.retry:
        held = waiting()
        sent, failed = drain(eid) if eid else (0, [])
        left = waiting()
        if not held:
            print("nothing was waiting to send")
        elif not left:
            print(f"sent {sent} finding(s) that were waiting")
        else:
            # "sent 0" used to mean both "the spool was empty" and "the retry
            # failed". Reading the first as the second is how a block ends
            # believing its findings landed.
            print(f"! {left} of {held} finding(s) could NOT be sent, and are still waiting:",
                  file=sys.stderr)
            for w in why_lines(failed):
                print(f"    {w}", file=sys.stderr)
        total = table_count(eid, seat(c)) if eid else None
        if total is not None:
            print(f"{ENTITY} holds {total} finding(s) for seat {seat(c)}")
        return 1 if left else 0

    if a.file:
        items = json.loads(pathlib.Path(a.file).read_text(encoding="utf-8-sig"))
    else:
        s = a.summary
        if a.summary_file:
            s = pathlib.Path(a.summary_file).read_text(encoding="utf-8-sig")
        if not (a.block and a.category and s):
            ap.error("need --block, --category and --summary (or --file)")
        ev = a.evidence
        if a.evidence_file:
            ev = pathlib.Path(a.evidence_file).read_text(encoding="utf-8-sig")
        items = [{"block": a.block, "category": a.category, "summary": s,
                  "source": a.source, "ask": a.ask, "artifact": a.artifact, "evidence": ev}]

    ctx = context(c, a)
    optional = ("block", "category", "summary", "source", "ask", "artifact", "evidence")
    rows = [{**ctx, "processed": False,
             **{k: i[k] for k in optional if i.get(k) is not None}}
            for i in items]

    if eid:
        drained, _ = drain(eid)
        sent, failed = insert(eid, rows, c.get("entityFields"), c.get("entityLimits"))
        if not failed:
            extra = f" (plus {drained} recovered from the spool)" if drained else ""
            print(f"logged {len(sent)} finding(s) to {ENTITY}{extra}")
            return 0
        for w in why_lines(failed):
            print(f"! {w}", file=sys.stderr)
        if sent:
            print(f"  {len(sent)} of {len(rows)} landed; only the rest are spooled.", file=sys.stderr)
        rows = [r for r, _ in failed]
    spool(rows)
    print(f"spooled {len(rows)} finding(s); {waiting()} now waiting. "
          f"Run 'python3 log-finding.py --retry' before you finish the block.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
