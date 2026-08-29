#!/usr/bin/env python3
"""Structural gate for a Case Management SDD, in about a second and without a tenant.

**Why this exists.** `uipath-maestro-case` will not check your design — it trusts
`sdd.md` as written, greps for the four headings and one task block, and never
compares it with the process. The planner's `audit_sdd.py` checks the shape; nothing
checks the design. What that cost when it was measured is in `method/sdd-guide.md`.

Nothing downstream reports any of it, because nothing downstream looks. This
script is the only thing between a plausible-looking design and that outcome, so
every rule below is a defect that really shipped.

  ./check_sdd.py sdd.md                    structure, bindings, reachability
  ./check_sdd.py sdd.md --pdd docs/pdd.md  also cross-check task type and SLAs
                                           against the PDD
  ./check_sdd.py sdd.md --entity contracts/claim-entity.md
                                           the Case Entity against the contract
                                           (found by itself when beside the SDD)

exit 0 clean · 1 failures · 2 could not read the file

FAIL is a defect that will reach the built plan. WARN is worth a look and does
not stop the build. NOTE is something the script could not decide — never a pass.
"""

import argparse, pathlib, re, sys
from collections import defaultdict

# The build reads these four headings and nothing else will do — the planner's case
# template writes them since CLI line 1.201; a hand-written or older design may not.
SECTIONS = ["## Section 1: Case Definition", "## Section 2: Stages & Tasks",
            "## Section 3: Personas & App Views", "## Section 4: Integrations"]
SUBHEADS = ["### Case Metadata", "### Case Variables", "### Case Exit Conditions"]
TASK_TYPES = {"action", "process", "agent", "rpa", "api-workflow", "case-management",
              "execute-connector-activity", "wait-for-connector", "wait-for-timer"}
# Judgement work must not land on a deterministic runner, and vice versa.
JUDGEMENT_TYPES = {"agent"}
DETERMINISTIC_TYPES = {"rpa", "api-workflow", "execute-connector-activity"}

# The six provided Orchestrator automations (contracts/provided-processes.md) — for TYPE-4.
PROVIDED = ["Retrieve Property Claim", "Extract Claim Data", "Retrieve Policy Document",
            "Retrieve Previous Claims", "Retrieve Inspection Report", "Client Notification"]

# Their argument names, as `uip or packages entry-points` returned them on 2026-08-28 at the
# versions then deployed (propery-insurance-claims 1.0.36 · Extract.Claim.Data._IXP_ 1.0.2 ·
# Retrieve.Policy.Document, Retrieve.Previous.Claims, Retrieve.Inspection.Report 1.0.0 ·
# Client.Notification 1.1.4) — for ARG-1. The contract says the platform is authoritative:
# if entry-points disagrees with this list, the platform wins, this list is updated, and the
# disagreement is logged. A design that binds a name outside it (Terra01 bound 11 of 16 to
# names it recalled — `out_PolicyData` does not exist) faults on the first claim at 3e.
PROVIDED_ARGS = {
    "in_Scenario", "in_Discrepancy", "in_ClaimID", "in_ProfileId", "in_Seed", "out_ClaimID",   # Retrieve Property Claim
    "out_PolicyID", "out_ClaimIXPDataJSON", "out_ClaimFormPDF",              # Extract Claim Data (IXP)
    "in_PolicyID", "out_PolicyPDF",                                          # Retrieve Policy Document
    "out_PreviousClaimsJSON",                                                # Retrieve Previous Claims
    "out_ReportReady", "out_AssessmentReport",                               # Retrieve Inspection Report
    "in_Body", "in_Subject", "in_Recepient", "in_ClaimId",                   # Client Notification
}

# Names a bare call inside an `=js:` expression may legitimately start with — for JS-1.
# Anything else (`currencyToCountry(…)`, `nowIso()`, `finalizeDecision(…)`) is a helper the
# design assumed exists; the expression grammar has none, and the write it feeds yields nothing.
JS_GLOBALS = {"JSON", "Number", "String", "Boolean", "Math", "Date", "Array", "Object", "parseInt",
              "parseFloat", "isNaN", "isFinite", "RegExp", "Set", "Map", "BigInt", "Symbol", "Error",
              "encodeURIComponent", "decodeURIComponent", "String.raw", "Intl"}


def gateway_outputs(sdd_path):
    """The task outputs `contracts/review-task.md` pins, read from the contract beside the SDD
    when it exists; the pinned names otherwise (one fact, one home — the contract is the home)."""
    fallback = ["reviewDecision", "reviewerNotes", "reviewedAt", "settlementJson"]
    try:
        c = (pathlib.Path(sdd_path).resolve().parent / "contracts" / "review-task.md").read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return fallback
    names = re.findall(r'^\|\s*\*\*output\*\*\s*\|\s*`([A-Za-z]+)`', c, re.M)
    return names or fallback


STOP = set("the a an and or of to for it its is are be this that with from into on in by "
           "at as every each any all not no its their his her them they we you your our".split())


class Report:
    def __init__(self):
        self.rows = []

    def add(self, sev, rule, msg):
        self.rows.append((sev, rule, msg))

    def emit(self):
        order = {"FAIL": 0, "WARN": 1, "NOTE": 2}
        for sev, rule, msg in sorted(self.rows, key=lambda r: order[r[0]]):
            print(f"{sev:4}  {rule:<12} {msg}")
        n = sum(1 for s, _, _ in self.rows if s == "FAIL")
        w = sum(1 for s, _, _ in self.rows if s == "WARN")
        t = sum(1 for s, _, _ in self.rows if s == "NOTE")
        if not self.rows:
            print("clean — structure, bindings and reachability all check out")
        else:
            print(f"\n{n} failure(s), {w} warning(s), {t} note(s)")
        return 1 if n else 0


def tasks_of(text):
    """Every `##### Task N.M: name` block, with the body up to the next task or stage."""
    out = []
    marks = [(m.start(), m.group(1), m.group(2).strip())
             for m in re.finditer(r'^##### Task ([\w.]+):\s*(.*)$', text, re.M)]
    bounds = [m.start() for m in re.finditer(r'^(##### Task |### |## )', text, re.M)]
    for pos, num, name in marks:
        nxt = next((b for b in bounds if b > pos), len(text))
        out.append({"num": num, "name": name, "body": text[pos:nxt]})
    return out


def words(s):
    return {w for w in re.findall(r'[a-z]+', s.lower()) if w not in STOP and len(w) > 2}


def check_structure(text, r):
    for h in SECTIONS:
        if h not in text:
            r.add("FAIL", "SHAPE-1", f"missing heading {h!r} — the build reads these four verbatim. "
                                     "a design without them is built thinly rather than refused")
    for h in SUBHEADS:
        if h not in text:
            r.add("FAIL", "SHAPE-2", f"missing {h!r} under Section 1")
    ts = tasks_of(text)
    if not ts:
        r.add("FAIL", "SHAPE-3", "no `##### Task N.M:` detail blocks. A summary table is not a design — "
                                 "the build has nothing per-task to read")
    if not re.search(r'^### (Stage|Secondary Stage)', text, re.M):
        r.add("FAIL", "SHAPE-4", "no `### Stage` blocks")
    return ts


def check_planner_audit(sdd_path, r):
    """Run the planner's own shape audit so the designer runs one command. SHAPE-5 carries its
    findings; a missing audit script is a note, not a pass."""
    import os, subprocess
    audit = next((pth for pth in (os.path.expanduser("~/.agents/skills/uipath-planner/scripts/audit_sdd.py"),
                                   os.path.expanduser("~/.uipath/.skills/skills/uipath-planner/scripts/audit_sdd.py")) if os.path.exists(pth)), None)
    if not audit:
        r.add("NOTE", "SHAPE-0", "the planner's audit_sdd.py was not found — run `uip skills install`, then the audit by hand")
        return
    res = subprocess.run([sys.executable, audit, sdd_path], capture_output=True, text=True)
    out = (res.stdout + res.stderr).strip()
    if res.returncode != 0 or "AUDIT FAIL" in out:
        lines = [l.strip() for l in out.splitlines() if l.strip() and "AUDIT FAIL" not in l]
        r.add("FAIL", "SHAPE-5", "the planner's audit fails: " + " · ".join(lines[:6]))


def check_handoff(text, r):
    if "<!-- planner-handoff:v1 -->" not in text:
        r.add("WARN", "HANDOFF-1", "no `<!-- planner-handoff:v1 -->` marker — task derivation will not "
                                   "recognise this as a planner SDD")
    if re.search(r'Status.{0,12}\bdraft\b', text, re.I) and not re.search(r'Status.{0,12}\bready\b', text, re.I):
        r.add("FAIL", "HANDOFF-2", "Status is `draft` — downstream skills refuse to build from a draft")
    # Anchored to the SME review table's own `Blocking` column. The earlier form failed any
    # `| Yes |` row — every task envelope has one — whenever the word "blocking" appeared in
    # the 1,200 characters before it, so a design could fail for prose (Opus03, 2026-08-28).
    sme = re.search(r'^#{1,6} [^\n]*SME Review[^\n]*\n(.*?)(?=^#{1,6} |\Z)', text, re.M | re.S)
    rows = [l for l in sme.group(1).splitlines() if l.strip().startswith("|")] if sme else []
    if rows:
        header = [c.strip().lower() for c in rows[0].strip().strip("|").split("|")]
        if "blocking" in header:
            col = header.index("blocking")
            for row in rows[2:]:
                cells = [c.strip().lower() for c in row.strip().strip("|").split("|")]
                if len(cells) > col and cells[col] == "yes":
                    r.add("FAIL", "HANDOFF-3", "an SME review item is still marked Blocking = yes")
                    break


def check_tasks(tasks, r):
    for t in tasks:
        m = re.search(r'\*\*Type:\*\*\s*`?([a-z-]+)`?', t["body"])
        if not m:
            r.add("FAIL", "TYPE-1", f"Task {t['num']} ({t['name'][:44]}) has no **Type:**")
            continue
        ty = m.group(1)
        t["type"] = ty
        if ty not in TASK_TYPES:
            r.add("FAIL", "TYPE-2", f"Task {t['num']} type {ty!r} is not one of the nine the build accepts")
        # an action task with no outcome named is a human gate nobody can answer
        if ty == "action" and not re.search(r'\*\*Actions:?\*\*|\| *Button *\|', t["body"]):
            r.add("WARN", "TYPE-3", f"Task {t['num']} is `action` but names no outcome buttons")
        # Measured 2026-08-27 on the participant tenant: a `process` task resolves against
        # processOrchestration-index.json, which is empty there; the six provided Orchestrator
        # automations live in process-index.json and bind only as `rpa`. Eight tasks typed
        # `process` packed, validated and would have bound nothing.
        if ty == "process" and any(name.lower() in t["body"].lower() for name in PROVIDED):
            r.add("WARN", "TYPE-4", f"Task {t['num']} ({t['name'][:40]}) binds a provided Orchestrator automation as "
                                    "`process` — on this tenant that resolves against an empty registry; bind it as `rpa` "
                                    "(measured 2026-08-27, `3d-case/cookbook.md`)")
        # The two gateways bind contracts/review-task.md; a renamed output binds to nothing,
        # silently, and re-registering the app later clears both gateways. Measured: an SDD
        # named the second gate's settlement output `approvedSettlement` for `settlementJson`.
        if ty == "action":
            want = gateway_outputs(t.get("_sdd_path"))
            # The first gate writes the eligibility* columns, the second the review* ones
            # (claim-entity.md: "the two gates do not share columns"), so each contract name
            # is satisfied by its eligibility counterpart too. settlementJson exists only at
            # the gate whose outcomes are Approve/Deny.
            alt = {"reviewDecision": "eligibilityDecision", "reviewerNotes": "eligibilityNotes",
                   "reviewedAt": "eligibilityReviewedAt"}
            second_gate = re.search(r'\bApprove\b', t["body"]) and re.search(r'\bDeny\b', t["body"])
            outs = re.search(r'\*\*Output(?: Schema)?s?:?\*\*(.*?)(?:\n\*\*|\n#####|\Z)', t["body"], re.S)
            haystack = outs.group(1) if outs else t["body"]   # the table, not the prose around it
            missing = []
            for w in want:
                if w == "settlementJson" and not second_gate:
                    continue
                if w == "reviewedAt":      # the case may stamp the time itself at the write
                    continue
                names = [w] + ([alt[w]] if w in alt else [])
                # the decision arrives as the platform's literal `Action` output mapped
                # `-> reviewDecision`, so the name may be a field or a binding target
                if not any(re.search(r'\b' + re.escape(n) + r'\b', haystack) for n in names):
                    missing.append(w)
            if missing:
                r.add("FAIL", "ACT-1", f"Task {t['num']} ({t['name'][:40]}) is a gateway and its block never names "
                                       f"{', '.join('`'+w+'`' for w in missing)} — `contracts/review-task.md` spells the outputs "
                                       "the case binds; a different name binds to nothing")
        # this is what produced three tasks with every input blank
        ins = re.search(r'\*\*Inputs:?\*\*(.*?)(?:\n\*\*|\Z)', t["body"], re.S)
        if ins:
            rows = [l for l in ins.group(1).split("\n")
                    if l.strip().startswith("|") and not re.match(r'^\|[-\s|:]+\|$', l.strip())]
            rows = [l for l in rows if not re.search(r'\|\s*Field\s*\|', l, re.I)]
            blank = [l for l in rows if re.match(r'^\|[^|]+\|[^|]*\|\s*(—|-|)\s*\|?\s*$', l.strip())]
            if rows and len(blank) == len(rows):
                r.add("FAIL", "BIND-1", f"Task {t['num']} declares {len(rows)} input(s) and binds none of them")


def check_bindings(text, r, tasks):
    """Outputs must map with `->` or `=`. A bare field name means something else."""
    for t in tasks:
        outs = re.search(r'\*\*Outputs:?\*\*(.*?)(?:\n\*\*|\n#|\Z)', t["body"], re.S)
        if not outs:
            continue
        for line in outs.group(1).split("\n"):
            s = line.strip()
            if not s.startswith("|") or re.match(r'^\|[-\s|:]+\|$', s):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 2 or cells[0].lower() in ("field", ""):
                continue
            if cells[1] in ("—", "-", ""):
                continue
            if "->" not in cells[1] and "=" not in cells[1]:
                r.add("FAIL", "BIND-2", f"Task {t['num']} output {cells[0]!r} binds as {cells[1]!r} — "
                                        "an output row needs `->` or `=`; a bare name is not a mapping")
            # `x = ""` passes BIND-2 and is never what anyone meant: an empty literal is the
            # one value that *destroys* a field's content rather than leaving it alone, and a
            # task declaring a variable it does not produce is claiming another step's output.
            m2 = re.match(r'^\s*(\w+)\s*=\s*(""|\'\')\s*$', cells[1])
            if m2:
                r.add("FAIL", "BIND-6", f"Task {t['num']} output assigns {m2.group(1)!r} an empty literal — "
                                        "an empty string destroys content rather than leaving it unset, and a "
                                        "task that declares a variable it does not produce is claiming another "
                                        "step's output")

    # every consumed variable needs a producer
    declared, produced = set(), set()
    block = re.search(r'### Case Variables(.*?)(?=\n## |\n### |\Z)', text, re.S)
    if block:
        for line in block.group(1).split("\n"):
            s = line.strip()
            if s.startswith("|") and not re.match(r'^\|[-\s|:]+\|$', s):
                cells = [c.strip().strip("`") for c in s.strip("|").split("|")]
                if cells and cells[0].lower() not in ("name", ""):
                    declared.add(cells[0])
                    # BIND-3 (retired 2026-08-27, number kept): it demanded a quoted Default because
                    # the 1.199 case template said so. The 1.201 planner template writes the plain
                    # value and the build string-encodes it (global-vars/planning.md: "always written
                    # as a quoted string ... string-encoding overrides"). The rule now fires nothing.
                    has_trigger = len(cells) >= 4 and cells[3] not in ("", "—", "-")
                    has_default = len(cells) >= 6 and cells[5] not in ("", "—", "-")
                    # an `In` argument is produced by the trigger even when sourceTriggers is blank —
                    # blank means "the primary trigger" in the template's grammar
                    is_in_arg = len(cells) >= 2 and cells[1].lower() == "in"
                    if has_trigger or has_default or is_in_arg:
                        produced.add(cells[0])
    produced |= set(re.findall(r'->\s*`?(\w+)`?', text))
    # `| — | claimVar = "value" |` assigns as much as `-> claimVar` does, and an action
    # task's outcome buttons assign under **Actions:** rather than **Outputs:**.
    for t in tasks:
        for head in (r'\*\*Outputs:?\*\*', r'\*\*Output Schema:?\*\*', r'\*\*Actions:?\*\*'):
            blk = re.search(head + r'(.*?)(?:\n\*\*|\n#|\Z)', t["body"], re.S)
            if blk:
                produced |= set(re.findall(r'`?(\w+)`?\s*=(?!=)', blk.group(1)))
    # every read — `=vars.x` bindings and `vars.x` inside `=js:` expressions and conditions;
    # a stage entry on `=js:vars.missingRequiredDocument` that nothing declares passed here
    # until 2026-08-28 (Terra01 run 2)
    reads = set(re.findall(r'=vars\.(\w+)', text)) | set(re.findall(r'`=js:[^`\n]*?\bvars\.(\w+)', text))
    for m in re.finditer(r'`=js:([^`\n]*)`', text):
        reads |= set(re.findall(r'\bvars\.(\w+)', m.group(1)))
    for v in sorted(reads):
        if v in declared and v not in produced:
            r.add("FAIL", "BIND-4", f"`vars.{v}` is read but nothing produces it — no output row, "
                                    "no default, no trigger field")
        elif v not in declared:
            r.add("FAIL", "BIND-5", f"`vars.{v}` is read but never declared in Case Variables — "
                                    "the name resolves to nothing at runtime")


def _outputs_section(body):
    m = re.search(r'\*\*Output(?: Schema)?s?:?\*\*(.*?)(?:\n\*\*|\n#|\Z)', body, re.S)
    return m.group(1) if m else body


def check_platform_fidelity(text, r, tasks):
    """What the two gates could not see on 2026-08-28: an SDD that passed both and was not
    buildable — arguments bound to names the automations do not have, `=js:` helpers that do
    not exist, gateways that never read the platform's `Action` output. Added after the
    Terra01 / Opus03 comparison (lab findings 223)."""
    # ARG-1 — every in_/out_ name in an `rpa` task block is one the six automations have.
    for t in tasks:
        if t.get("type") != "rpa":
            continue
        # only the argument column — the first cell of a table row — not prose or `=vars.out_X`
        # references to another task's outputs inside the mapping cells
        firsts = [re.sub(r'`', '', ln.strip().strip('|').split('|')[0]).strip()
                  for ln in t["body"].split("\n") if ln.strip().startswith("|")]
        names = sorted({f for f in firsts if re.fullmatch(r'(?:in|out)_[A-Za-z][A-Za-z0-9]*', f)} - PROVIDED_ARGS)
        if names:
            r.add("FAIL", "ARG-1", f"Task {t['num']} ({t['name'][:40]}) binds {', '.join(names)} — not an argument "
                                   "of any provided automation at the recorded versions. Read them from "
                                   "`uip or packages entry-points`, never from memory; if the platform "
                                   "disagrees with this checker, the platform wins — log it")
    # JS-1 — a bare call in an `=js:` expression is a helper nobody defined.
    unknown = {}
    for m in re.finditer(r'`=js:([^`\n]*)`', text):   # expressions are backticked; prose that mentions =js: is not
        for c in re.finditer(r'(?<![\.\w$])([A-Za-z_$][A-Za-z0-9_$]*)\s*\(', m.group(1)):
            name = c.group(1)
            if name in JS_GLOBALS or name in ("if", "for", "while", "switch", "return", "function", "typeof"):
                continue
            unknown.setdefault(name, text.count("\n", 0, m.start()) + 1)
    for name, line in sorted(unknown.items(), key=lambda kv: kv[1]):
        r.add("FAIL", "JS-1", f"`{name}(…)` is called in an =js: expression (first at line {line}) and is not "
                              "defined anywhere the case can see — write the logic inline or in an agent")
    # ACT-2 — a gateway's outputs must map the platform's literal `Action` (contracts/review-task.md).
    for t in tasks:
        if t.get("type") == "action" and not re.search(r'\bAction\b', _outputs_section(t["body"])):
            r.add("FAIL", "ACT-2", f"Task {t['num']} ({t['name'][:40]}) is a gateway and its outputs never map the "
                                   "platform's `Action` output — the decision reaches no variable and every "
                                   "claim takes the same branch while the plan looks correct")
    # ROUTE-1 — a skip or exit condition written against the outcome not wanted passes when unset.
    hits = []
    for m in re.finditer(r'`=js:[^`\n]*?!==?\s*(?:true|"[A-Za-z ]+"|\'[A-Za-z ]+\')', text):
        hits.append(text.count("\n", 0, m.start()) + 1)
    if hits:
        r.add("WARN", "ROUTE-1", f"{len(hits)} condition(s) are written against a value (`!== …`) at line(s) "
                                 f"{', '.join(map(str, hits[:6]))}{'…' if len(hits) > 6 else ''} — an unset variable "
                                 "passes such a test. Check the direction of each: opening a human gate on `!== true` "
                                 "is safe (unset → human); skipping one on `!== \"Deny\"` is not (unset → skipped). "
                                 "3e-run/cookbook.md, *A routing guard sends a claim down the wrong lane*")
    # BUDGET-1 — an agent task that states no input size cannot be checked against the ~8,700 cap.
    for t in tasks:
        if t.get("type") != "agent":
            continue
        # a size is a number that is not the cap itself — "at most 8,700" states nothing (Terra01 run 2)
        sizes = [int(n.replace(",", "")) for n in re.findall(r'\b(\d{1,3}(?:,\d{3})+|\d{3,5})\b(?=.{0,24}(?:char|byte))', t["body"], re.I | re.S)]
        sizes = [n for n in sizes if n >= 100 and n not in (8700, 10000)]
        if not sizes:
            r.add("WARN", "BUDGET-1", f"Task {t['num']} ({t['name'][:40]}) is an agent and states no input size of its own — "
                                      "quoting the cap is not a budget; the ~8,700-character cap on its summed inputs is "
                                      "unverified (contracts/claim-entity.md, *Two budgets*)")
    # INPUT-1 — an agent, connector or rpa task needs an Inputs table with rows, not a sentence.
    # Run 2 of Terra01 had wrong names in its tables and answered by deleting the tables.
    for t in tasks:
        if t.get("type") not in ("agent", "execute-connector-activity", "rpa"):
            continue
        m = re.search(r'\*\*Inputs?:?\*\*(.*?)(?:\n\*\*|\n#|\Z)', t["body"], re.S)
        rows = [l for l in (m.group(1).split("\n") if m else []) if l.strip().startswith("|") and not re.match(r'^\|[-\s|:]+\|$', l.strip())]
        if len(rows) < 2:   # header + at least one field
            r.add("FAIL", "INPUT-1", f"Task {t['num']} ({t['name'][:40]}) is `{t['type']}` and has no Inputs table — a sentence "
                                     "under **Inputs:** binds nothing; the build needs a row per field (name, type, binding)")
    # HANDOFF-4 — the header may say `Template validation | passed` only if the planner's audit passes.
    if re.search(r'Template validation\*?\*?\s*\|\s*passed', text, re.I):
        import shutil, subprocess, os
        audit = next((pth for pth in (os.path.expanduser("~/.agents/skills/uipath-planner/scripts/audit_sdd.py"),
                                       os.path.expanduser("~/.uipath/.skills/skills/uipath-planner/scripts/audit_sdd.py")) if os.path.exists(pth)), None)
        if audit and tasks and tasks[0].get("_sdd_path"):
            res = subprocess.run([sys.executable, audit, tasks[0]["_sdd_path"]], capture_output=True, text=True)
            if res.returncode != 0 or "AUDIT FAIL" in (res.stdout + res.stderr):
                r.add("FAIL", "HANDOFF-4", "the Planner Handoff header says `Template validation | passed` and the planner's "
                                           "audit_sdd.py exits non-zero — run the audit, repair, then flip the header")
        elif not audit:
            r.add("NOTE", "HANDOFF-4", "cannot find the planner's audit_sdd.py to confirm `Template validation | passed`")
    # PROGRESS-1 — the record is written as you go; its absence at gate time is worth a line.
    if tasks and tasks[0].get("_sdd_path"):
        import pathlib as _pl
        if not (_pl.Path(tasks[0]["_sdd_path"]).resolve().parent / "PROGRESS.md").exists():
            r.add("NOTE", "PROGRESS-1", "no PROGRESS.md beside sdd.md — the next block starts from what is written there, "
                                        "and a compaction takes everything that is not (AGENTS.md)")


def _declared_vars(text):
    out = set()
    block = re.search(r'### Case Variables(.*?)(?=\n## |\n### |\Z)', text, re.S)
    for line in (block.group(1).split("\n") if block else []):
        st = line.strip()
        if st.startswith("|") and not re.match(r'^\|[-\s|:]+\|$', st):
            cells = [c.strip().strip("`") for c in st.strip("|").split("|")]
            if cells and cells[0].lower() not in ("name", ""):
                out.add(cells[0])
    return out


def check_design_safety(text, r, tasks):
    """Terra01 run 3 (2026-08-28) met every rule above with real work and was still not buildable:
    eleven `x = =js:true` outputs to undeclared variables, gateways whose entry and skip conditions
    were both equality tests, no §7.9 in any agent block, no slice guard anywhere (lab findings 232)."""
    declared = _declared_vars(text)
    # BIND-7 — an `=` output row assigns a variable that Case Variables never declares.
    seen = set()
    for t in tasks:
        for head in (r'\*\*Outputs:?\*\*', r'\*\*Output Schema:?\*\*', r'\*\*Actions:?\*\*'):
            blk = re.search(head + r'(.*?)(?:\n\*\*|\n#|\Z)', t["body"], re.S)
            if not blk:
                continue
            for name in re.findall(r'`?\b([A-Za-z_]\w*)`?\s*=(?!=)\s*`?=?', blk.group(1)):
                if name in declared or name in seen or name in ("Action",) or name.lower() in ("value", "default", "type"):
                    continue
                seen.add(name)
                r.add("FAIL", "BIND-7", f"Task {t['num']} ({t['name'][:40]}) assigns `{name}` in an output row and Case Variables "
                                        "never declares it — io-binding has no companion for the `=`; the row is dropped or faults")
    # ROUTE-2 — the same flag tested `=== true` to open a gate and `=== false` to skip it leaves the
    # unset case to neither: the stage stalls instead of routing to the human.
    opens = set(re.findall(r'`=js:\s*vars\.(\w+)\s*===\s*true\s*`', text))
    skips = set(re.findall(r'`=js:\s*vars\.(\w+)\s*===\s*false\s*`', text))
    for v in sorted(opens & skips):
        r.add("FAIL", "ROUTE-2", f"`vars.{v}` opens on `=== true` and skips on `=== false` — a value that never lands satisfies "
                                 "neither, and the claim stalls. One side must be the complement (`!== true` opens the human gate)")
    # NATURE-4 — PDD §7.9 says what is not a finding; an agent that never hears it flags every claim.
    agents = [t for t in tasks if t.get("type") == "agent"]
    if agents and not any(re.search(r'7\.9|not a finding|BR-7[0-8]', t["body"]) for t in agents):
        r.add("WARN", "NATURE-4", "no agent task block cites PDD §7.9 / *what is not a finding* — the clean claim will not come back "
                                  "silent unless every analysis agent carries those rules")
    # BUDGET-2 — JSON envelopes bound into agents, and no `.slice(` anywhere.
    envelopes = any(re.search(r'\*\*Inputs?:?\*\*.*?\bvars\.\w*Json\b', t["body"], re.S) for t in agents)
    if envelopes and ".slice(" not in text:
        r.add("WARN", "BUDGET-2", "JSON envelopes are bound into agents and nothing in the design slices — an envelope over the cap "
                                  "faults the call (a 400 at 10,000 serialised characters); guard the producer writes or the consumer inputs")


def check_reachability(text, r):
    block = re.search(r'### Case Exit Conditions(.*?)(?=\n### |\n## |\Z)', text, re.S)
    if block:
        whens = []
        for line in block.group(1).split("\n"):
            s = line.strip()
            if s.startswith("|") and not re.match(r'^\|[-\s|:]+\|$', s):
                cells = [c.strip().strip("`") for c in s.strip("|").split("|")]
                if cells and cells[0].lower() not in ("when", ""):
                    whens.append(cells[0])
        if len(whens) > 1 and len(set(whens)) == 1:
            r.add("FAIL", "EXIT-1", f"all {len(whens)} case-exit rows fire on the same event "
                                    f"({whens[0]!r}) — only the first can ever decide the outcome")
        if whens and not any("required-stages-completed" in w for w in whens):
            r.add("WARN", "EXIT-2", "no `required-stages-completed` exit row — normal completion is unmodelled")

    for m in re.finditer(r'^### (?:Secondary )?Stage[^\n]*?:\s*(.+)$', text, re.M):
        start = m.start()
        nxt = text.find("\n### ", start + 1)
        body = text[start: nxt if nxt > 0 else len(text)]
        if "#### Stage Entry Conditions" not in body:
            r.add("WARN", "STAGE-1", f"stage {m.group(1).strip()[:44]!r} declares no entry conditions")


def check_sla_fidelity(text, pdd, r):
    """An SLA the PDD never asked for is over-design that fires escalations nobody wants.

    Measured 2026-08-25: two correct-shaped designs of the same PDD, one carrying the
    five stage SLAs the PDD gives and one carrying eight. The three extra were invented.
    This is `uipath-review`'s **Extra** category — the one the shipped tooling misses.
    """
    want = set()
    for line in pdd.split("\n"):
        m = re.match(r'^\|\s*Stage \d+\s*[—-]\s*([^|]+?)\s*\|', line.strip())
        if m:
            want.add(m.group(1).strip().lower())
    if not want:
        return
    # stage headings carry an id in parentheses in some designs — `Intake (`stage-intake`)`
    marks = [(m.start(), re.sub(r'\s*\([^)]*\)\s*$', '', m.group(1)).strip().strip('`').strip())
             for m in re.finditer(r'^### (?:Secondary Stage|Stage \d+)\s*:?\s*(.+)$', text, re.M)]
    for i, (pos, name) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        has = re.search(r'^#### Stage SLA\s*$', text[pos:end], re.M) is not None
        n = name.lower().strip()
        if has and n not in want:
            r.add("WARN", "SLA-1", f"stage {name!r} carries an SLA the PDD does not give it — "
                                   "an invented deadline escalates to someone who never asked to be told")
        if not has and n in want:
            r.add("FAIL", "SLA-2", f"stage {name!r} has an SLA in the PDD and none in the design")


def check_case_sla(text, pdd, r):
    """The whole-claim SLA is a number a business user signed. `SLA-1`/`SLA-2` cover the
    stage rows; nothing covered the case-level one, and a design that quietly moved it
    passed clean.

    Measured 2026-08-27, twice: two independent designs of PDD 1.0 (whole claim 8 days,
    stages summing to 21) each set the case SLA to 21 and disclosed it in Design Feedback
    — correctly. The PDD was re-baselined to 25. A third design that had *not* disclosed
    the change would have passed every rule here. Disclosed is a WARN (a re-baseline is
    owed before the build binds it); silent is a FAIL.
    """
    m = re.search(r'^\|\s*Whole claim[^|]*\|\s*(\d+)\s*(?:business\s+)?days?\s*\|', pdd, re.M | re.I)
    if not m:
        return
    want = int(m.group(1))
    d = re.search(r'^\|\s*Case-Level SLA\s*\|\s*([^|]+?)\s*\|', text, re.M)
    if not d:
        r.add("WARN", "SLA-3", f"the PDD gives the whole claim {want} business days (§5.5) and "
                               "Case Metadata carries no `Case-Level SLA` row")
        return
    cell = d.group(1)
    n = re.search(r'P(\d+)D\b', cell) or re.search(r'(\d+)\s*(?:d\b|days?\b|business\s+days?\b)', cell, re.I)
    if not n:
        r.add("NOTE", "SLA-3", f"Case-Level SLA {cell!r} is not a day count this script can compare "
                               f"with the PDD's {want} business days")
        return
    got = int(n.group(1))
    if got == want:
        return
    fb = re.search(r'^## Design Feedback to PDD\s*$', text, re.M)
    disclosed = False
    if fb:
        end = text.find("\n## ", fb.end())
        seg = text[fb.end(): end if end > 0 else len(text)]
        for row in seg.split("\n"):                    # one feedback row must own this change
            if row.startswith("|") and re.search(r'5\.5', row) and (
                    re.search(rf'\b{got}\b', row) or re.search(r'whole[- ]claim|case-level|case sla', row, re.I)):
                disclosed = True
                break
    if disclosed:
        r.add("WARN", "SLA-3", f"Case-Level SLA is {got} days; the PDD signs {want} business days (§5.5). "
                               "Disclosed in Design Feedback — a business-process change: the PDD is "
                               "re-baselined and re-signed before the build binds this number")
    else:
        r.add("FAIL", "SLA-3", f"Case-Level SLA is {got} days; the PDD signs {want} business days (§5.5) and "
                               "Design Feedback does not say so — a signed number changed silently")


def _entity_columns(md):
    """Column names from `contracts/claim-entity.md`: every backticked identifier in the
    first *and third* cells of its column tables (one table pairs two columns per row)."""
    cols, col_cells = set(), []
    for line in md.split("\n"):
        if not line.startswith("|"):
            col_cells = []                              # a blank or prose line ends the table
            continue
        cells = _cells(line)
        if cells and cells[0] == "Column":              # a header row opens a column table —
            col_cells = [i for i, c in enumerate(cells) if c == "Column"]  # one table pairs two per row
            continue
        if col_cells and line.startswith("| `"):
            for i in col_cells:
                if i < len(cells):
                    cols.update(re.findall(r'`([a-zA-Z][A-Za-z0-9]*)`', cells[i]))
    return cols


def check_entity_contract(text, contract, r):
    """The claim entity is a component boundary (Locked 58): `3b-entity` builds it from
    `contracts/claim-entity.md`, the case writes it, the app reads it. A column the design
    adds is a column the build never creates — the write faults at run time, three blocks
    after the design passed. A column the design drops is a screen field nobody fills.
    """
    want = _entity_columns(contract)
    if not want:
        r.add("NOTE", "ENT-0", "could not read any column from the entity contract")
        return
    i = text.find("### Case Entity")
    if i < 0:
        return  # the addendum's absence is TBL/OWN territory, not this rule's
    j = text.find("\n### ", i + 1)
    body = text[i: j if j > 0 else len(text)]
    got = set()
    for line in body.split("\n"):
        m = re.match(r'^\|\s*`?([a-zA-Z][A-Za-z0-9]*)`?\s*\|', line)
        if m and m.group(1) not in ("Field", "Column", "Name"):
            got.add(m.group(1))
    if not got:
        return
    for c in sorted(got - want):
        r.add("FAIL", "ENT-1", f"column `{c}` is in the design's Case Entity and not in "
                               "`contracts/claim-entity.md` — `3b-entity` will not create it and the "
                               "first write to it faults at run time")
    for c in sorted(want - got):
        r.add("WARN", "ENT-2", f"contract column `{c}` is missing from the design's Case Entity — "
                               "nothing will write it")


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _table(text, header_pat):
    """Rows of the first table whose header row matches, as lists of cells."""
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and header_pat.search(ln):
            hdr, rows = _cells(ln), []
            # a real design interleaves notes and blockquotes between rows, so run
            # to the next heading rather than stopping at the first non-row line
            for nxt in lines[i + 2:]:
                t = nxt.strip()
                if t.startswith("#"):
                    break
                if t.startswith("|"):
                    rows.append(_cells(nxt))
            return hdr, rows
    return None, []


def _owners(cell):
    """The task ids an owner cell names. The case itself normalises to CASE."""
    ids = set(re.findall(r"\bS?\d+\.\d+\b", cell))
    if not ids and re.search(r"\bcase\b|\bevery stage\b", cell, re.I):
        return {"CASE"}
    return ids


def check_table_integrity(text, r):
    """A table interrupted mid-way renders its remaining rows as literal text.

    Markdown ends a table at the first line that is not a row, so a note or a
    blockquote placed between rows turns everything below it into a paragraph of
    pipes — confirmed against GitHub's own renderer. Measured 2026-08-26: a design
    put an explanatory blockquote inside its Write-Ownership Matrix, and the seven
    rows below it — every column the human review path writes — stopped being a
    table. They are invisible to a reader skimming the tables and to any tool that
    parses them, which is how a contradiction survives review in the first place.

    Put the note above the table or below it, never inside it.
    """
    lines, i, fence = text.split("\n"), 0, False
    while i < len(lines):
        t = lines[i].strip()
        if t.startswith("```"):
            fence = not fence
            i += 1
            continue
        if fence or not t.startswith("|"):
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].strip().startswith("|"):
            j += 1
        block = lines[i:j]
        if not any(re.fullmatch(r"\|[\s:|-]+\|", b.strip()) for b in block):
            first = block[0].strip()
            r.add("FAIL", "TBL-1",
                  f"{len(block)} row(s) with no header above them render as literal "
                  f"text, not a table — {first[:70]}... "
                  "A note between rows ends the table; move it above or below")
        i = j


def check_write_ownership(text, r):
    """Two tables naming different writers for the same column is a design that contradicts itself.

    Measured 2026-08-26 on a real build: the Case Entity table gave three envelope
    columns to tasks 4.1, 4.2 and 4.4 — their producers — while the Write-Ownership
    Matrix forty lines below gave all three to task 5.1, which never reads them. The
    build follows the matrix, so 5.1 was handed three 10,000-character columns as
    inputs and **could not start**: a component's inputs are capped near 8,700 all
    together. The gate passed both versions, which is why this rule exists.

    Whichever table is right, disagreement is the defect — it is caught here in a
    second, or at 3d as a component that will not run.
    """
    # the header must carry both, or `| Field | Value |` in the handoff block wins
    hdr_e, ent = _table(text, re.compile(r"\|\s*Field\s*\|.*\|\s*Written by\s*\|"))
    hdr_m, mat = _table(text, re.compile(r"\|\s*Entity\.Field\s*\|"))
    if hdr_m is None or hdr_e is None:
        return  # not every design carries both tables
    wi = hdr_e.index("Written by")

    declared = {}
    for row in ent:
        if len(row) > wi and re.fullmatch(r"[a-z][A-Za-z0-9]*", row[0]):
            declared[row[0]] = _owners(row[wi])

    assigned = {}
    for row in mat:
        if len(row) < 2:
            continue
        for f in re.findall(r"\.([a-zA-Z][A-Za-z0-9]*)", row[0]):
            assigned[f] = _owners(row[1])

    for f in sorted(set(declared) & set(assigned)):
        a, b = declared[f], assigned[f]
        if a and b and a != b:
            r.add("FAIL", "OWN-1",
                  f"{f}: the Case Entity table says {', '.join(sorted(a))} writes it, "
                  f"the Write-Ownership Matrix says {', '.join(sorted(b))}. "
                  "The build follows the matrix — if that owner does not already consume "
                  "the column, it is handed one it never reads")
    for f in sorted(set(declared) - set(assigned)):
        r.add("WARN", "OWN-2", f"{f} is a column with no row in the Write-Ownership Matrix — "
                               "nothing declares who owns the write")


def check_nature(text, pdd, r, tasks):
    """The check that catches a design shaped by what was lying around the tenant.

    The PDD's Decision-nature column is the whole reason it can drive a design:
    *rule-expressible* work belongs on a deterministic runner, *judgement* work on
    an agent. Measured 2026-08-25 — a design took its task types from agents that
    happened to be deployed nearby and put settlement arithmetic on an agent,
    saying so outright. Nothing else in the toolchain would have noticed.
    """
    steps = []
    for line in pdd.split("\n"):
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) >= 5 and re.match(r'^\d+\.\d+$', cells[0]):
            nature = cells[4].lower()
            kind = ("judgement" if "judgement" in nature
                    else "rule" if "rule-expressible" in nature else "na")
            # every step joins the pool, including n/a — otherwise a task matches the
            # nearest *rated* step instead of its own and is judged against it
            steps.append({"id": cells[0], "action": cells[1], "kind": kind, "w": words(cells[1])})
    if not steps:
        r.add("NOTE", "NATURE-0", "no Decision-nature rows found in the PDD — cross-check skipped")
        return

    by_id = {st["id"]: st for st in steps}
    # The agents the contract pins. Two of them do work the PDD marks rule-expressible
    # (settlement arithmetic, the decision rules) — accepted knowingly for the workshop
    # (Locked 57), so on those the mismatch is a warning to confirm reproducibility,
    # not a failure. Any *other* judgement runner on rule work still fails.
    pinned = set()
    for cand in (pathlib.Path(__file__).resolve().parent.parent / "contracts" / "components.md",
                 pathlib.Path("contracts/components.md")):
        if cand.exists():
            pinned = set(re.findall(r'^\| `(\w+)` \|', cand.read_text(), re.M))
            break

    unmapped, unmapped_names = 0, []
    for t in tasks:
        if "type" not in t:
            continue
        # 1. an explicit citation in the task block — `PDD step 4.3`, `PDD §5.3 steps 1.1 and 1.2`
        refs = re.findall(r'PDD (?:§5\.3 )?steps? ((?:\d+\.\d+)(?:(?:,| and) \d+\.\d+)*)', t["body"])
        ids = re.findall(r'\d+\.\d+', " ".join(refs))
        matched = [by_id[i] for i in ids if i in by_id]
        # 2. otherwise word overlap of the task name plus its rationale against the step's action,
        #    relative to the smaller word set so a three-word task name can still match
        if not matched:
            # the task name first — a three-word name matching two of a step's words is a match;
            # the rationale only as a fallback, and only on three or more shared words, because
            # rationales mention neighbouring steps and a loose match judges a task by the wrong row
            nw = words(t["name"])
            rat = re.search(r'\*\*Design Rationale:\*\*(.*?)(?:\n\*\*|\n#|\Z)', t["body"], re.S)
            rw = nw | (words(rat.group(1)[:300]) if rat else set())
            best, score = None, 0.0
            for st in steps:
                if not st["w"] or not nw:
                    continue
                shared_name = len(nw & st["w"])
                shared_all = len(rw & st["w"])
                ov = shared_name / min(len(st["w"]), len(nw))
                if ov < 0.5 and shared_all >= 3:
                    ov = 0.5 + shared_all / (10 * len(st["w"]))
                if ov > score:
                    best, score = st, ov
            if best and score >= 0.5:
                matched = [best]
        if not matched:
            unmapped += 1
            unmapped_names.append(f"{t['num']} {t['name'][:30]}")
            continue
        for best in matched:
            if best["kind"] == "na":
                continue      # the PDD rates no decision here, so no type follows from it
            if best["kind"] == "rule" and t["type"] in JUDGEMENT_TYPES:
                on_pinned = any(a in t["body"] or a.lower() in t["name"].lower().replace(" ", "") for a in pinned)
                sev = "WARN" if on_pinned else "FAIL"
                tail = (" — the contract pins this agent (Locked 57), so the arithmetic rides a judgement "
                        "runner on purpose: keep temperature 0 and prove the numbers reproduce"
                        if on_pinned else
                        " — deterministic work on a judgement runner is how arithmetic stops being reproducible")
                r.add(sev, "NATURE-1", f"Task {t['num']} ({t['name'][:40]}) is `{t['type']}` but PDD step "
                                       f"{best['id']} marks it rule-expressible{tail}")
            # a connector write persists a decision somebody else made; only a runner that
            # computes — rpa, api-workflow — can be wrongly asked to weigh a judgement
            if best["kind"] == "judgement" and t["type"] in DETERMINISTIC_TYPES - {"execute-connector-activity"}:
                r.add("FAIL", "NATURE-2", f"Task {t['num']} ({t['name'][:40]}) is `{t['type']}` but PDD step "
                                          f"{best['id']} marks it judgement — a rule engine cannot weigh "
                                          "what that step is asked to weigh")
    if unmapped:
        r.add("NOTE", "NATURE-3", f"{unmapped} task(s) could not be matched to a PDD step — their type was "
                                  f"not checked. Not a pass. Cite `PDD step N.N` in each task's Design "
                                  f"Rationale and this goes to zero. Unmatched: {', '.join(unmapped_names[:8])}")


def main():
    ap = argparse.ArgumentParser(description="Structural gate for a Case Management SDD.")
    ap.add_argument("sdd")
    ap.add_argument("--pdd", help="cross-check task type against the PDD's Decision nature")
    ap.add_argument("--entity", help="the claim-entity contract to check the Case Entity against "
                                     "(default: contracts/claim-entity.md beside the SDD, when it exists)")
    a = ap.parse_args()
    try:
        text = open(a.sdd, encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read {a.sdd}: {e}", file=sys.stderr)
        return 2

    r = Report()
    tasks = check_structure(text, r)
    for t in tasks:
        t["_sdd_path"] = a.sdd
    check_planner_audit(a.sdd, r)
    check_handoff(text, r)
    check_tasks(tasks, r)
    check_bindings(text, r, tasks)
    check_platform_fidelity(text, r, tasks)
    check_design_safety(text, r, tasks)
    check_reachability(text, r)
    check_table_integrity(text, r)
    check_write_ownership(text, r)
    if a.pdd:
        try:
            pdd_text = open(a.pdd, encoding="utf-8").read()
            check_nature(text, pdd_text, r, tasks)
            check_sla_fidelity(text, pdd_text, r)
            check_case_sla(text, pdd_text, r)
        except OSError as e:
            r.add("NOTE", "NATURE-0", f"cannot read {a.pdd}: {e}")
    entity = pathlib.Path(a.entity) if a.entity else pathlib.Path(a.sdd).resolve().parent / "contracts" / "claim-entity.md"
    if a.entity or entity.exists():
        try:
            check_entity_contract(text, entity.read_text(encoding="utf-8"), r)
        except OSError as e:
            r.add("NOTE", "ENT-0", f"cannot read {entity}: {e}")
    return r.emit()


if __name__ == "__main__":
    sys.exit(main())
