#!/usr/bin/env python3
"""Resolve every IXP path the design and the case plan read against a real extraction payload.

The design reaches into the extracted claim with `=js:` expressions such as

    =js:(vars.claimDataJson?.ClaimIncident?.[0]?.TypeOfIncident?.Value || "")

and every one of them is optional-chained, so a **wrong key never throws** -- the
binding silently yields "" or undefined and the failure surfaces stages later as
an Agent reasoning about a claim with no incident type. Measured 2026-08-27: a
design derived the keys from the taxonomy labels and got three of them wrong
(`TypeofIncident`, `DateofIncident`, `DateofSubmission`); nothing threw. This
script is how that is caught mechanically rather than by eye -- run it at `3a`
against a payload from your own extraction, and again whenever a later block
adds a binding that reads the extraction.

    python3 3a-extraction/check_extraction_keys.py <payload.json> [more.json ...] [sdd.md] [caseplan.case ...]

With no `.md` / `.case` argument it reads `sdd.md` at the seat root and every
`Build/**/caseplan.case`. A payload file is the `out_ClaimIXPDataJSON` object of an
`Extract Claim Data (IXP)` job, saved as JSON:

    uip or jobs get <job-key> --output json | python3 -c \
      'import json,sys; print(json.dumps(json.loads(json.load(sys.stdin)["Data"]["OutputArguments"])["out_ClaimIXPDataJSON"]))' \
      > payload.json

What counts as a read of the payload: a path off `vars.claimData` / `vars.claimDataJson`,
off whatever variable the design or plan binds `out_ClaimIXPDataJSON` to, or off the
output name itself (`response.out_ClaimIXPDataJSON...`); and, inside one `=js:` expression,
a path through an alias (`const c = vars.claimData?.ClaimClaimant?.[0]; c?.EmailAddress`),
a destructuring, or the element of an array method over a payload array
(`(... || []).map(r => r.EstimatedCost.Value.Value)` reads `ClaimDamageInventory[0]...`).
Static analysis, no JS engine: anything it cannot follow is a NOTE, never a guess.

Exit 0 when every path resolves on every payload, 1 otherwise.
"""

import json
import pathlib
import re
import sys

SEAT = pathlib.Path(__file__).resolve().parent.parent
SDD = SEAT / "sdd.md"
OUTPUT = "out_ClaimIXPDataJSON"

# `out_ClaimIXPDataJSON` is an OBJECT, so a design that follows contracts/claim-entity.md holds it
# in `claimData` and keeps `claimDataJson` for the stringified copy that lands in the column; plans
# in the wild use either name for the object. Both are roots by default, plus any variable the design
# (`out_ClaimIXPDataJSON -> x`) or the plan (`"var": "x"` on that output) binds it to.
DEFAULT_VARS = {"claimData", "claimDataJson"}

IDENT = r"[A-Za-z_$][\w$]*"
# One step of a member chain: `.Key`, `?.Key`, `[0]`, `?.[0]`, `["Key"]`, `[i]` (a variable index).
ACC = re.compile(r"(?:\?\.|\.)(" + IDENT + r")|(?:\?\.)?\[\s*(?:(\d+)|\"([^\"]*)\"|'([^']*)'|(" + IDENT + r"))\s*\]")
METHOD = re.compile(r"\s*\??\.\s*(" + IDENT + r")\s*\(")
DEFAULT = re.compile(r"\s*(?:\?\?|\|\|)\s*(?:\[\s*\]|\{\s*\}|null\b|undefined\b|\"\s*\"|'\s*')")
TERM = re.compile(r"\s*(?:[;,)\]}]|$|\?\?|\|\|)")
CONSUMED = re.compile(r"\s*\??\.\s*(?:length\b|" + IDENT + r"\s*\()")

# Array methods whose callback gets an element, and which parameters are the element.
CALLBACK = {"map": {0}, "flatMap": {0}, "filter": {0}, "forEach": {0}, "some": {0}, "every": {0},
            "find": {0}, "findLast": {0}, "findIndex": {0}, "findLastIndex": {0},
            "reduce": {1}, "reduceRight": {1}, "sort": {0, 1}, "toSorted": {0, 1}}
SAME_ARRAY = {"filter", "slice", "sort", "toSorted", "reverse", "toReversed"}  # result is still the array
ONE_ELEMENT = {"find", "findLast"}                                              # result is one element

PATHS = {}   # chain tuple -> {"src": first source text, "where": [file:line, ...]}
NOTES = []   # (where, message, chain or None) -- printed when chain is None or reaches an object/array


def mask(src):
    """Blank string, regex and comment contents (same length), so a quote or paren in them is not code."""
    out, i, n, last = list(src), 0, len(src), ""

    def blank(a, b):
        for k in range(a, min(b, n)):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        c = src[i]
        if c in "\"'`":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            blank(i + 1, j)
            i, last = j + 1, c
        elif src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            blank(i, j)
            i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            blank(i, j)
            i = j
        elif c == "/" and (last == "" or last in "(,=:[!&|?{};+-*%<>~^"
                           or re.search(r"\b(?:return|typeof|case)\s*$", src[max(0, i - 10):i])):
            j, in_class = i + 1, False
            while j < n and src[j] != "\n":
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == "[":
                    in_class = True
                elif src[j] == "]":
                    in_class = False
                elif src[j] == "/" and not in_class:
                    break
                j += 1
            blank(i + 1, j)
            i, last = j + 1, "/"
        else:
            if not c.isspace():
                last = c
            i += 1
    return "".join(out)


def split_top(s):
    """Split on commas outside brackets."""
    parts, depth, cur = [], 0, ""
    for ch in s:
        depth += ch in "([{"
        depth -= ch in ")]}"
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    return parts + [cur]


def strip_default(p):
    """`x = []` -> `x` (a top-level `=` that is not `==` or `=>`)."""
    depth = 0
    for k, ch in enumerate(p):
        depth += ch in "([{"
        depth -= ch in ")]}"
        if ch == "=" and depth == 0 and p[k + 1:k + 2] not in ("=", ">") and p[k - 1:k] not in ("=", "!", "<", ">"):
            return p[:k]
    return p


class Unit:
    """One expression (a `=js:` body, a fenced block, or plain text) and what is bound inside it."""

    def __init__(self, text, js, file, line0, root):
        self.O, self.js, self.file, self.line0, self.root = text, js, file, line0, root
        self.M = mask(text) if js else text
        self.open_of, self.close_of, self.pairs, stack = {}, {}, [], []
        for k, ch in enumerate(self.M):
            if ch in "([{":
                stack.append((k, ch))
            elif ch in ")]}" and stack and "([{"[")]}".index(ch)] == stack[-1][1]:
                o = stack.pop()[0]
                self.open_of[k], self.close_of[o] = o, k
                self.pairs.append((o, k))
        self.bindings = []   # (name, start, end, chain or None) -- None shadows an outer alias
        self.refs = []       # (pos, chain, consumed) of every payload reference
        self.unbound = []    # (names, rhs start, rhs end) of declarations that touch the payload unresolved
        self.params = []     # (open, close) of every parameter list -- a parameter is not a read

    def where(self, pos):
        return f"{self.file}:{self.line0 + self.O.count(chr(10), 0, pos)}"

    def enclosing_close(self, pos):
        inner = [c for o, c in self.pairs if o < pos < c]
        return min(inner) if inner else len(self.M)

    def bind(self, name, start, end, chain):
        self.bindings.append((name, start, end, chain))

    def lookup(self, name, pos):
        best = None
        for n, s, e, chain in self.bindings:
            if n == name and s <= pos < e and (best is None or s >= best[0]):
                best = (s, chain)
        return None if best is None else best[1]

    def shadow(self, text, start, end):
        for name in re.findall(IDENT, text):
            self.bind(name, start, end, None)

    # --- references ---------------------------------------------------------------------------

    def accessors(self, j):
        """The member chain starting at j: (steps, end). Stops before a method call or `.length`."""
        steps = []
        while True:
            m = ACC.match(self.M, j)
            if not m:
                return steps, j
            if m.group(1) is not None:
                if m.group(1) == "length" or re.match(r"\s*\(", self.M[m.end():]):
                    return steps, j
                steps.append(m.group(1))
            elif m.group(2) is not None:
                steps.append(int(m.group(2)))
            elif m.group(3) is not None or m.group(4) is not None:
                g = 3 if m.group(3) is not None else 4
                steps.append(self.O[m.start(g):m.end(g)])
            else:
                steps.append("*")   # a variable index or key: element 0 of an array, unknown on an object
            j = m.end()

    def record(self, chain, start, end):
        entry = PATHS.setdefault(tuple(chain), {"src": self.O[start:end].strip(), "where": []})
        w = self.where(start)
        if w not in entry["where"]:
            entry["where"].append(w)

    def ref(self, i):
        """A payload reference at i: (chain, end of its own steps, end after array calls, consumed)."""
        m = re.compile(r"JSON\.parse\(\s*(?:" + self.root + r")\s*\)").match(self.M, i) if self.js else None
        m = m or re.compile(self.root).match(self.M, i)
        if m:
            base, j = [], m.end()
        else:
            m = re.compile(IDENT).match(self.M, i)
            base = self.lookup(m.group(), i) if (self.js and m) else None
            if base is None:
                return None
            j = m.end()
        steps, j = self.accessors(j)
        chain = base + steps
        if steps:
            self.record(chain, i, j)
        if not self.js:
            return chain, j, j, False
        if re.search(r"Object\.(?:keys|values|entries)\(\s*$", self.M[max(0, i - 30):i]):
            NOTES.append((self.where(i), f"`{self.O[i:j].strip()}` is iterated by key; the keys read are not checked", chain))
        chain, end = self.follow(i, j, chain)
        consumed = bool(CONSUMED.match(self.M, end))
        self.refs.append((i, chain, consumed))
        return chain, j, end, consumed

    def follow(self, start, end, chain):
        """Walk `?? []`, a wrapping `( )` and array methods after a payload reference; bind callbacks."""
        while True:
            m = DEFAULT.match(self.M, end)
            j = m.end() if m else end
            close = re.match(r"\s*\)", self.M[j:])
            if close:
                c = j + close.end() - 1
                o = self.open_of.get(c)
                if o is not None and self.M[o + 1:start].strip() == "":
                    start, end = o, c + 1
                    continue
            m = METHOD.match(self.M, end)
            if not m or m.group(1) not in CALLBACK.keys() | SAME_ARRAY:
                return chain, end
            o = m.end() - 1
            c = self.close_of.get(o, len(self.M) - 1)
            if m.group(1) in CALLBACK:
                self.callback(o + 1, chain + [0], CALLBACK[m.group(1)])
            if m.group(1) not in SAME_ARRAY | ONE_ELEMENT:
                return chain, end
            if m.group(1) in ONE_ELEMENT:
                chain = chain + [0]
            steps, after = self.accessors(c + 1)
            if steps:
                self.record(chain + steps, start, after)
            chain, end = chain + steps, after

    def callback(self, i, element, params):
        """Bind the element parameter(s) of an inline callback `r => ...`, `(t, r) => ...`, `function (r)`."""
        m = re.compile(r"\s*(?:async\s+)?(?:function\s*(?:" + IDENT + r")?\s*(\()|(\()|(" + IDENT + r")\s*=>)").match(self.M, i)
        if not m:
            NOTES.append((self.where(i), "an array of the payload is passed to a callback that is not inline; what it reads is not checked", element[:-1]))
            return
        if m.group(3):
            start, text = m.start(3), m.group(3)
        else:
            start = m.start(1) if m.group(1) else m.start(2)
            if not m.group(1) and not re.match(r"\s*=>", self.M[self.close_of.get(start, start) + 1:]):
                NOTES.append((self.where(i), "an array of the payload is passed to a callback that is not inline; what it reads is not checked", element[:-1]))
                return
            text = self.M[start + 1:self.close_of.get(start, start)]
        end = self.scope_end(start)
        for k, p in enumerate(split_top(text)):
            if k in params:
                self.pattern(p, element, start, end)
            else:
                self.shadow(p, start, end)

    def scope_end(self, start):
        """Where a parameter list at start stops being in scope: a function body, or the enclosing group."""
        if self.M[start] == "(" and re.search(r"\bfunction\s*(?:" + IDENT + r")?\s*$", self.M[max(0, start - 40):start]):
            body = re.match(r"\s*\{", self.M[self.close_of.get(start, start) + 1:])
            if body:
                return self.close_of.get(self.close_of[start] + body.end(), len(self.M))
        return self.enclosing_close(start)

    def pattern(self, p, chain, start, end):
        """Bind a name or a destructuring pattern to a payload chain."""
        p = strip_default(p).strip()
        if not p:
            return
        if re.fullmatch(IDENT, p):
            self.bind(p, start, end, chain)
        elif p.startswith("{") and p.endswith("}"):
            for part in split_top(p[1:-1]):
                key, sep, target = part.partition(":")
                key = strip_default(key).strip()
                if not key or key.startswith("..."):
                    self.shadow(key, start, end)
                elif not re.fullmatch(IDENT, key):
                    self.shadow(part, start, end)
                    NOTES.append((self.where(start), f"destructured key `{key.strip()}` is not checked", None))
                else:
                    self.pattern(target if sep else key, chain + [key], start, end)
        elif p.startswith("[") and p.endswith("]"):
            for k, part in enumerate(split_top(p[1:-1])):
                if part.strip().startswith("..."):
                    self.shadow(part, start, end)
                else:
                    self.pattern(part, chain + [k], start, end)
        else:
            self.shadow(p, start, end)
            NOTES.append((self.where(start), f"pattern `{p[:40]}` bound to the payload is not followed", None))

    def declaration(self, k):
        """`const|let|var x = <payload path>` and `for (const r of <payload array>)`: returns where to resume."""
        m = re.compile(r"\s*(" + IDENT + r"|[{\[])").match(self.M, k)
        if not m:
            return k
        p = m.start(1)
        after = self.close_of.get(p, p) + 1 if m.group(1) in "{[" else m.end(1)
        pat = self.M[p:after]
        m = re.compile(r"\s*(=(?![=>])|of\b)").match(self.M, after)
        if not m:
            return after
        of = m.group(1) == "of"
        q = re.compile(r"[\s(]*").match(self.M, m.end()).end()
        r = self.ref(q)
        if of:
            fo = max((o for o, c in self.pairs if o < k < c and self.M[o] == "("), default=None)
            body = re.match(r"\s*\{", self.M[self.close_of[fo] + 1:]) if fo is not None else None
            scope = self.close_of.get(self.close_of[fo] + body.end(), len(self.M)) if body else self.enclosing_close(k)
        else:
            scope = self.enclosing_close(k)
        if r and not r[3] and TERM.match(self.M, r[2]):
            self.pattern(pat, r[0] + [0] if of else r[0], r[2], scope)
            return r[1]
        self.shadow(pat, m.end(), scope)
        e = m.end()
        while e < len(self.M) and self.M[e] not in ";,)]}":
            e = self.close_of.get(e, e) + 1 if self.M[e] in "([{" else e + 1
        self.unbound.append((pat.strip(), m.end(), e))
        return r[1] if r else q

    def analyse(self):
        if not self.js:
            for m in re.finditer(self.root, self.M):
                self.ref(m.start())
            return
        for m in re.finditer(r"=>", self.M):   # every arrow parameter shadows an outer alias of that name
            back = self.M[:m.start()].rstrip()
            if back.endswith(")") and len(back) - 1 in self.open_of:
                o = self.open_of[len(back) - 1]
                self.params.append((o, len(back) - 1))
                self.shadow(self.M[o + 1:len(back) - 1], o, self.enclosing_close(o))
            else:
                mi = re.search(IDENT + r"$", back)
                if mi:
                    self.params.append((mi.start(), mi.end()))
                    self.bind(mi.group(), mi.start(), self.enclosing_close(mi.start()), None)
        for m in re.finditer(r"\bfunction\s*(?:" + IDENT + r")?\s*\(", self.M):
            o = m.end() - 1
            self.params.append((o, self.close_of.get(o, o)))
            self.shadow(self.M[o + 1:self.close_of.get(o, o)], o, self.scope_end(o))
        resume = 0
        for m in re.finditer(IDENT, self.M):
            i = m.start()
            if i < resume:
                continue
            before = self.M[:i].rstrip()
            if before.endswith(".") and not before.endswith("..."):
                continue   # a member name, not a variable
            if m.group() in ("const", "let", "var"):
                resume = self.declaration(m.end())
                continue
            r = self.ref(i)
            if r:
                resume = r[1]
        for names, s, e in self.unbound:
            for pos, chain, consumed in self.refs:
                if s <= pos < e and not consumed and not any(o <= pos <= c for o, c in self.params):
                    NOTES.append((self.where(pos), f"`{names}` takes part of the payload through an expression this checker does not follow; paths read through it are not checked", chain))


def root_pattern(names):
    return (r"(?<![\w$.])(?:vars\??\.(?:" + "|".join(sorted(map(re.escape, names))) + r")(?![\w$])"
            r"|(?:" + IDENT + r"\??\.)*" + OUTPUT + r"(?![\w$]))")


def bound_names(files):
    """The variables the design or plan binds `out_ClaimIXPDataJSON` to."""
    names = set(DEFAULT_VARS)
    for f in files:
        text = f.read_text(encoding="utf-8")
        if f.suffix == ".md":
            names |= set(re.findall(OUTPUT + r"[\s`|]*" + "(?:->|=>|\u2192)" + r"[\s`|]*(?:vars\.)?(" + IDENT + ")", text))
            continue
        try:
            stack = [json.loads(text)]
        except ValueError:
            continue
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                if isinstance(node.get("var"), str) and any(
                        str(node.get(k, "")).lstrip("=") == OUTPUT for k in ("name", "id", "originalVar", "source", "target")):
                    names.add(node["var"])
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
    return names


def read_sources(files, root):
    for f in files:
        lines = f.read_text(encoding="utf-8").split("\n")
        if f.suffix != ".md":
            for n, line in enumerate(lines, 1):   # a case plan: every JSON string is one expression
                for lit in re.finditer(r'"(?:[^"\\]|\\.)*"', line):
                    try:
                        s = json.loads(lit.group())
                    except ValueError:
                        continue
                    if "=js:" in s:
                        Unit(s.split("=js:", 1)[1], True, f.name, n, root).analyse()
                    elif re.search(root, s):
                        Unit(s, False, f.name, n, root).analyse()
            continue
        n = 0
        while n < len(lines):
            line = lines[n]
            if line.lstrip().startswith("```"):   # a fenced block is one expression, aliases span its lines
                end = next((k for k in range(n + 1, len(lines)) if lines[k].lstrip().startswith("```")), len(lines))
                block = "\n".join(lines[n + 1:end])
                if re.search(root, block):
                    Unit(block.replace("=js:", "    "), True, f.name, n + 2, root).analyse()
                n = end + 1
                continue
            rest, pos = list(line), 0
            for m in re.finditer(r"=js:", line):
                if m.start() < pos:
                    continue
                if m.start() and line[m.start() - 1] == "`":
                    e = line.find("`", m.end())
                else:
                    e = line.find("=js:", m.end())
                e = len(line) if e < 0 else e
                Unit(line[m.end():e].replace("\\|", "|"), True, f.name, n + 1, root).analyse()
                rest[m.start():e] = " " * (e - m.start())
                pos = e
            Unit("".join(rest), False, f.name, n + 1, root).analyse()
            n += 1


def show(chain):
    out = ""
    for s in chain:
        if isinstance(s, int):
            out += f"[{s}]"
        elif s == "*":
            out += "[*]"
        elif re.fullmatch(IDENT, s):
            out += ("." if out else "") + s
        else:
            out += f"[{json.dumps(s)}]"
    return out


def resolve(payload, chain):
    """Walk the chain the way optional chaining does: (value, None) or (None, index of the step that misses).

    A variable index takes element 0 of an array; on an object it is unknowable: (None, "dynamic")."""
    node = payload
    for k, step in enumerate(chain):
        if step == "*":
            if not isinstance(node, list):
                return None, "dynamic"
            step = 0
        if isinstance(step, int):
            if not isinstance(node, list) or step >= len(node):
                return None, k
        elif not isinstance(node, dict) or step not in node:
            return None, k
        node = node[step]
    return node, None


def main():
    try:
        sys.stdout.reconfigure(errors="replace")   # a claimant's name must not crash a Windows console
    except AttributeError:
        pass
    args = [pathlib.Path(a) for a in sys.argv[1:]]
    payload_files = [a for a in args if a.suffix not in (".md", ".case")]
    sources = [a for a in args if a.suffix in (".md", ".case")]
    if not payload_files:
        print(__doc__)
        return 2
    if not sources:
        sources = ([SDD] if SDD.exists() else []) + sorted(
            p for p in SEAT.glob("Build/**/caseplan.case") if "node_modules" not in p.parts)
    for s in sources:
        if not s.exists():
            print(f"no such file: {s}")
            return 2
    read_sources(sources, root_pattern(bound_names(sources)))
    names = ", ".join(s.name for s in sources) or "nothing"
    if not PATHS:
        print(f"no payload paths found in {names} -- has the design stopped reading the extraction?")
        return 1

    payloads = [(str(a), json.loads(a.read_text(encoding="utf-8"))) for a in payload_files]
    seen = set()
    for where, msg, chain in NOTES:
        reaches = chain is None or any(isinstance(resolve(p, chain)[0], (dict, list)) for _, p in payloads)
        if reaches and (where, msg) not in seen:
            seen.add((where, msg))
            print(f"NOTE  {where}  {msg}")
    if seen:
        print()

    bad = empty = 0
    for arg, payload in payloads:
        print(f"=== {arg} -- {len(PATHS)} distinct path(s) from {names} ===")
        for chain, entry in sorted(PATHS.items(), key=lambda kv: show(kv[0])):
            path, where = show(chain), " ".join(entry["where"][:6]) + (" ..." if len(entry["where"]) > 6 else "")
            src = entry["src"] if len(entry["src"]) <= 80 else entry["src"][:77] + "..."
            value, miss = resolve(payload, chain)
            if miss == "dynamic":
                print(f"  NOTE     {path} -- variable key on an object, not checked   ({where})")
            elif miss is not None:
                bad += 1
                print(f"  MISSING  {path} -- no {show(chain[miss:miss + 1]) or chain[miss]!r} under {show(chain[:miss]) or 'the payload'}   ({where} as `{src}`)")
            elif value in (None, "", {}, []):
                # The path exists and the model found nothing: a field blank on the form (a Hong Kong
                # address has no ZIP). A wrong key is MISSING, never EMPTY -- so this is a note, not a failure.
                empty += 1
                print(f"  EMPTY    {path} = {value!r}   ({where})")
            else:
                shown = str(value if not isinstance(value, (dict, list)) else json.dumps(value))
                print(f"  ok       {path} = {shown[:60]}{'...' if len(shown) > 60 else ''}")
        print()

    groups = {"Claim", "ClaimClaimant", "ClaimProperty", "ClaimIncident",
              "ClaimDamageInventory", "ClaimClaimTotals"}
    for arg, payload in payloads:
        missing = groups - set(payload)
        rows = len(payload.get("ClaimDamageInventory") or [])
        print(f"{arg}: groups present {len(payload)}/6"
              + (f", MISSING {sorted(missing)}" if missing else "")
              + f", damage rows {rows}"
              + (" -- a blob, not one row per item" if rows == 1 else ""))
        if missing or rows < 2:
            bad += 1

    print()
    print("every path resolves" if not bad else f"{bad} problem(s)")
    if empty:
        print(f"{empty} empty value(s) -- confirm each is blank on the form itself; the design must tolerate it")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
