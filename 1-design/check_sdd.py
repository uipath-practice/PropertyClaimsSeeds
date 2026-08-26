#!/usr/bin/env python3
"""Structural gate for a Case Management SDD, in about a second and without a tenant.

**Why this exists.** `uipath-maestro-case` will not check your design — it trusts
`sdd.md` as written and never gap-fills it, so a design in the wrong shape is not
rejected. It is **built, thinly, and validates clean.** What that cost when it was
measured is in `method/sdd-guide.md`, which opens with it.

Nothing downstream reports any of it, because nothing downstream looks. This
script is the only thing between a plausible-looking design and that outcome, so
every rule below is a defect that really shipped.

  ./check_sdd.py sdd.md                    structure, bindings, reachability
  ./check_sdd.py sdd.md --pdd docs/pdd.md  also cross-check task type against
                                           the PDD's Decision nature

exit 0 clean · 1 failures · 2 could not read the file

FAIL is a defect that will reach the built plan. WARN is worth a look and does
not stop the build. NOTE is something the script could not decide — never a pass.
"""

import argparse, re, sys
from collections import defaultdict

# The build reads these four headings and nothing else will do. The planner's
# numbered template (`## 1. Case Overview` …) is a different document.
SECTIONS = ["## Section 1: Case Definition", "## Section 2: Stages & Tasks",
            "## Section 3: Personas & App Views", "## Section 4: Integrations"]
SUBHEADS = ["### Case Metadata", "### Case Variables", "### Case Exit Conditions"]
TASK_TYPES = {"action", "process", "agent", "rpa", "api-workflow", "case-management",
              "execute-connector-activity", "wait-for-connector", "wait-for-timer"}
# Judgement work must not land on a deterministic runner, and vice versa.
JUDGEMENT_TYPES = {"agent"}
DETERMINISTIC_TYPES = {"rpa", "api-workflow", "execute-connector-activity"}

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
                                     "A planner-template SDD will be built thinly rather than refused")
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


def check_handoff(text, r):
    if "<!-- planner-handoff:v1 -->" not in text:
        r.add("WARN", "HANDOFF-1", "no `<!-- planner-handoff:v1 -->` marker — task derivation will not "
                                   "recognise this as a planner SDD")
    if re.search(r'Status.{0,12}\bdraft\b', text, re.I) and not re.search(r'Status.{0,12}\bready\b', text, re.I):
        r.add("FAIL", "HANDOFF-2", "Status is `draft` — downstream skills refuse to build from a draft")
    for m in re.finditer(r'^\|.*\|\s*(yes)\s*\|\s*$', text, re.M | re.I):
        if "blocking" in text[max(0, m.start() - 1200):m.start()].lower().split("## ")[-1]:
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
                    # Default is column 6 in the shipped template; a non-string default is deleted
                    if len(cells) >= 6 and cells[5] not in ("", "—", "-"):
                        d = cells[5]
                        if not (d.startswith('"') or d.startswith("'")):
                            r.add("FAIL", "BIND-3", f"variable {cells[0]!r} default {d!r} is not written as a "
                                                    "string — non-strings are dropped on serialization, so the "
                                                    "variable is null at runtime and its first reader fails")
                    has_trigger = len(cells) >= 4 and cells[3] not in ("", "—", "-")
                    has_default = len(cells) >= 6 and cells[5] not in ("", "—", "-")
                    if has_trigger or has_default:
                        produced.add(cells[0])
    produced |= set(re.findall(r'->\s*`?(\w+)`?', text))
    # `| — | claimVar = "value" |` assigns as much as `-> claimVar` does, and an action
    # task's outcome buttons assign under **Actions:** rather than **Outputs:**.
    for t in tasks:
        for head in (r'\*\*Outputs:?\*\*', r'\*\*Output Schema:?\*\*', r'\*\*Actions:?\*\*'):
            blk = re.search(head + r'(.*?)(?:\n\*\*|\n#|\Z)', t["body"], re.S)
            if blk:
                produced |= set(re.findall(r'`?(\w+)`?\s*=(?!=)', blk.group(1)))
    for v in sorted(set(re.findall(r'=vars\.(\w+)', text))):
        if v in declared and v not in produced:
            r.add("FAIL", "BIND-4", f"`vars.{v}` is read but nothing produces it — no output row, "
                                    "no default, no trigger field")
        elif v not in declared:
            r.add("FAIL", "BIND-5", f"`vars.{v}` is read but never declared in Case Variables — "
                                    "the name resolves to nothing at runtime")


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

    unmapped = 0
    for t in tasks:
        if "type" not in t:
            continue
        tw = words(t["name"])
        best, score = None, 0.0
        for st in steps:
            if not st["w"]:
                continue
            ov = len(tw & st["w"]) / len(st["w"])
            if ov > score:
                best, score = st, ov
        if not best or score < 0.5:
            unmapped += 1
            continue
        if best["kind"] == "na":
            continue      # the PDD rates no decision here, so no type follows from it
        if best["kind"] == "rule" and t["type"] in JUDGEMENT_TYPES:
            r.add("FAIL", "NATURE-1", f"Task {t['num']} ({t['name'][:40]}) is `{t['type']}` but PDD step "
                                      f"{best['id']} marks it rule-expressible — deterministic work on a "
                                      "judgement runner is how arithmetic stops being reproducible")
        if best["kind"] == "judgement" and t["type"] in DETERMINISTIC_TYPES:
            r.add("FAIL", "NATURE-2", f"Task {t['num']} ({t['name'][:40]}) is `{t['type']}` but PDD step "
                                      f"{best['id']} marks it judgement — a rule engine cannot weigh "
                                      "what that step is asked to weigh")
    if unmapped:
        r.add("NOTE", "NATURE-3", f"{unmapped} task(s) could not be matched to a PDD step by name — "
                                  "their type was not checked. Not a pass")


def main():
    ap = argparse.ArgumentParser(description="Structural gate for a Case Management SDD.")
    ap.add_argument("sdd")
    ap.add_argument("--pdd", help="cross-check task type against the PDD's Decision nature")
    a = ap.parse_args()
    try:
        text = open(a.sdd, encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read {a.sdd}: {e}", file=sys.stderr)
        return 2

    r = Report()
    tasks = check_structure(text, r)
    check_handoff(text, r)
    check_tasks(tasks, r)
    check_bindings(text, r, tasks)
    check_reachability(text, r)
    if a.pdd:
        try:
            pdd_text = open(a.pdd, encoding="utf-8").read()
            check_nature(text, pdd_text, r, tasks)
            check_sla_fidelity(text, pdd_text, r)
        except OSError as e:
            r.add("NOTE", "NATURE-0", f"cannot read {a.pdd}: {e}")
    return r.emit()


if __name__ == "__main__":
    sys.exit(main())
