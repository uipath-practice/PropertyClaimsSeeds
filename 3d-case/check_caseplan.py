#!/usr/bin/env python3
"""Referential integrity for a case plan, in about a second and without a tenant.

Two families of check, both paid for in real failures:

1. **`vars.X` has a declaring task** — the original guard against silent I/O loss
   (a task output is the only thing that makes `vars.X` exist).

2. **Everything a node points at exists** — added 2026-08-11 after three separate
   breakages that this file would have caught and did not:

   - a new stage with no `layout.nodes` entry **crashed the Studio Web designer
     outright** (`Cannot read properties of undefined (reading 'x')`), with an error
     naming nothing that appears in the plan;
   - moving a task between stages left two exit rules naming a task no longer in their
     stage, which the canvas showed as a red stage and an empty task picker;
   - the same move left the incoming edge pointing at the old stage, so the canvas drew
     the flow straight past the new one.

   None of these is a `vars.` problem, so the original check passed every time. All three
   are one question: does every id a node references still resolve?

`uip maestro case validate --strict --sdd sdd.md` is the gate and checks the plan against the
design; this script checks what it cannot see — layout, an output named off its argument, a
connector input without a target, a skip on a human gate, an `exited` rule on a stage that
completes, a payload never written, a file output the runtime cannot fill, a gate that opens
before its stage writes the record, a condition reading an output id that stays null. Run it
after every edit and before every pack.

    python3 check_caseplan.py "<path to caseplan.case>"
"""
import json, os, re, sys

try:
    sys.stdout.reconfigure(errors="replace")   # a cp1252 console must not crash on an arrow
except AttributeError:
    pass

path = sys.argv[1] if len(sys.argv) > 1 else next((p for p in ('caseplan.case', 'caseplan.json') if os.path.exists(p)), 'caseplan.case')
if path in ('-h', '--help'):
    print(__doc__.strip())
    sys.exit(0)
try:
    doc = json.load(open(path))
except FileNotFoundError:
    print(f'cannot read {path} — pass the path to your caseplan.case', file=sys.stderr)
    sys.exit(2)
except json.JSONDecodeError as e:
    print(f'{path} is not valid JSON: {e}', file=sys.stderr)
    sys.exit(2)
problems = []


def stage_refs(rule):
    """Stage ids a rule names — under BOTH spellings, which are a schema generation apart.

    Older schema generations write `selectedStageId`, a single string; current ones write
    `selectedStageIds`, a list. This script read only the plural for its first weeks, so on
    every CLI-authored plan the reference and reachability checks below matched nothing and
    reported a clean run without examining anything. Measured 2026-08-23 on two independent
    builds, both 23.0.0, both getting zero stage checking.
    """
    one = rule.get('selectedStageId')
    many = rule.get('selectedStageIds') or []
    if isinstance(many, str):
        many = [many]
    return ([one] if one else []) + list(many)

declared = set()
for node in doc['nodes']:
    for group in (node['data'].get('tasks') or []):
        for task in group:
            for out in (task['data'].get('outputs') or []):
                # Both, not one or the other. Which of `var` and `id` `=vars.X` resolves
                # against at run time is stated nowhere: this script once said `id`; the
                # skill's io-binding doc says a `->` extraction mints `id` from the schema
                # field while `var` names the case variable (findings 3d, 2026-08-27). Builds
                # that set the two equal for every `->` output have not been bitten. They
                # diverge when two tasks write the same payload -- the second gets a suffixed
                # id and keeps the shared var -- so declaring both is what avoids false alarms.
                declared.add(out.get('var'))
                declared.add(out.get('id'))
            declared.discard(None)

# The case's own arguments. A task output is not the only way a `vars.X` comes to
# exist: an In-argument declares three entries — a formal slot the caller writes at
# job start, a companion the plan reads by name, and a bridge on the trigger that
# copies one into the other. All three are legitimate declarations and the original
# check knew about none of them, so adding the first case argument made the script
# report four phantom undeclared variables.
for kind in ('inputs', 'outputs', 'inputOutputs'):
    for var in (doc.get('variables') or {}).get(kind) or []:
        declared.add(var.get('id') or var.get('var'))

# A bridge with no companion is the failure this section exists to catch: `=vars.X`
# resolves to undefined at run time and nothing says so.
for node in doc['nodes']:
    for bridge in ((node['data'].get('uipath') or {}).get('outputs') or []):
        target = bridge.get('var')
        if target and target not in declared:
            print(f'NO COMPANION trigger {node["id"]} writes vars.{target}, '
                  f'which no variables.inputOutputs entry declares')
            problems.append(target)

referenced = set(re.findall(r'vars\.([A-Za-z_][A-Za-z0-9_]*)', json.dumps(doc)))
missing = sorted(r for r in referenced if r not in declared)

# Known-good: set by the engine on first pass rather than declared as a task output.
missing = [m for m in missing if not m.startswith('stageHasRun_')]

for name in missing:
    print(f'UNDECLARED  vars.{name}')
print(f'{len(referenced)} referenced, {len(declared)} declared, {len(missing)} undeclared')
problems += [f'vars.{m}' for m in missing]

# ---------------------------------------------------------------- referential integrity

stages = [n for n in doc['nodes'] if n.get('type') == 'case-management:Stage']
node_ids = {n['id'] for n in doc['nodes']}
edges = doc.get('edges') or []
edge_ids = {e['id'] for e in edges}
layout = doc.get('layout') or {}

# Layout parity. A node absent from layout.nodes takes the designer down on load; the
# skill's advice to emit `layout: {}` holds only for a plan whose map is already empty.
if layout.get('nodes'):
    for nid in sorted(node_ids - set(layout['nodes'])):
        print(f'NO LAYOUT   node {nid} has no layout.nodes entry — the designer will crash on load')
        problems.append(nid)
    for nid in sorted(set(layout['nodes']) - node_ids):
        print(f'STALE       layout.nodes[{nid}] refers to no node')
        problems.append(nid)
if layout.get('edges'):
    for eid in sorted(edge_ids - set(layout['edges'])):
        print(f'NO LAYOUT   edge {eid} has no layout.edges entry')
        problems.append(eid)

# A rule may only name stages that exist. (A rule naming a task outside its own stage is
# `validate --strict`'s: "task selection missing".)
for stage in stages:
    label = stage['data'].get('label', stage['id'])
    for scope in ('entryConditions', 'exitConditions'):
        for cond in (stage['data'].get(scope) or []):
            for group in cond['rules']:
                for rule in group:
                    for ref in stage_refs(rule):
                        if ref not in node_ids:
                            print(f'BAD REF     {label}/{scope}/{cond["id"]} names stage {ref}, which does not exist')
                            problems.append(ref)

# Edges must join real nodes, and every edgeIds reference must resolve.
for edge in edges:
    for end in ('source', 'target'):
        if edge[end] not in node_ids:
            print(f'BAD EDGE    {edge["id"]} {end}={edge[end]} refers to no node')
            problems.append(edge['id'])
for stage in stages:
    for cond in (stage['data'].get('entryConditions') or []):
        for ref in (cond.get('edgeIds') or []):
            if ref not in edge_ids:
                print(f'BAD REF     {stage["data"].get("label")}/{cond["id"]} names edge {ref}, which does not exist')
                problems.append(ref)

# --------------------------------------------------- reachability: exited vs completed
#
# A stage that marks itself COMPLETE does not satisfy a `selected-stage-exited` entry rule
# on the far side. Cost two deploy cycles on 2026-08-11 and, before that, findings 13:
# both times the downstream stage simply never started — no error, no incident, no cursor,
# every task green. This is the check that would have caught it in a second.
#
# The inverse is fine and is used deliberately: a stage with no marks-complete exit (the
# Awaiting Assessment poll loop) is *only* reachable via `exited`. So is a gate stage whose
# refusal exit does not complete it beside a completing Proceed exit: the rule fires on the
# refusal. Only a stage whose every exit marks it complete can never be `exited`.

marks_complete = {
    s['id']: bool(exits) and all(c.get('marksStageComplete') for c in exits)
    for s in stages
    for exits in [s['data'].get('exitConditions') or []]
}
labels = {s['id']: s['data'].get('label', s['id']) for s in stages}

for stage in stages:
    for cond in (stage['data'].get('entryConditions') or []):
        for group in cond['rules']:
            for rule in group:
                if rule.get('rule') != 'selected-stage-exited':
                    continue
                expr = rule.get('conditionExpression') or ''
                # `=js:false`-style guards are the deliberately inert branches; skip them.
                if 'vars.' not in expr and 'false' in expr:
                    continue
                for src in stage_refs(rule):
                    if marks_complete.get(src):
                        print(f'UNREACHABLE {labels.get(stage["id"])} enters on exited({labels.get(src, src)}), '
                              f'but that stage marks itself COMPLETE — the rule never fires')
                        problems.append(cond['id'])

# ------------------------------------------------- bindings: the name has to be the real one
#
# Added 2026-08-20 after a plan that passed this script *and* `uip maestro case validate`
# faulted on its fourth task with `170002 ... Value for a required activity argument
# 'in_PolicyID' was not supplied`. Both classes below bind to nothing at run time and are
# invisible to every other gate, which is what makes them worth a second each here.

# 1. A process or agent output carries the automation's own argument name, `out_`-prefix
#    and all. Strip the prefix to something tidier -- `PolicyID` for `out_PolicyID` -- and
#    the output binds to nothing, the case variable stays empty, and the failure surfaces
#    one or more tasks later, on whoever first reads it.
ENGINE_SUPPLIED = {'Error', 'response'}

for node in doc['nodes']:
    for group in (node['data'].get('tasks') or []):
        for task in group:
            if task.get('type') not in ('process', 'rpa', 'agent'):
                continue
            for out in (task['data'].get('outputs') or []):
                name = out.get('name') or ''
                # A `custom` output is a value the plan computes from other variables --
                # its source is an expression, not an argument the automation declares --
                # so the naming rule below does not apply to it. Skipping these was added
                # 2026-08-20 after the check fired twice on a plan that was correct.
                if name in ENGINE_SUPPLIED or out.get('custom'):
                    continue
                if not name.startswith('out_'):
                    kind = task.get('type')
                    article = 'an' if kind and kind[0] in 'aeiou' else 'a'
                    print(f'BAD OUTPUT  {task["id"]}.{name} — {article} {kind} output is named for the '
                          f'automation argument it reads, so this should be out_{name}; as written it binds '
                          f'to nothing and vars.{out.get("var") or out.get("id")} stays empty')
                    problems.append(name)
                # A source that is not an expression is a deliberate literal seed (the poll
                # loop primes its flag with `false`), so only an expression is checked.
                elif str(out.get('source', '')).startswith('=') and out['source'] != '=' + name:
                    print(f'BAD OUTPUT  {task["id"]}.{name} has source {out["source"]!r}, expected {"=" + name!r}')
                    problems.append(name)

# 2. A connector activity's inputs are addressed by `target`, and their payload lives under
#    `body`. Write `value` instead -- the shape every other input in the plan uses -- and the
#    activity is dispatched with no query parameters at all. For a Data Fabric write that
#    surfaces as `[102003] Missing path variables in URL .../EntityService/{entityName}/insert`,
#    which reads as a missing entity name and is really a missing input.
for node in doc['nodes']:
    for group in (node['data'].get('tasks') or []):
        for task in group:
            if task.get('type') != 'execute-connector-activity':
                continue
            for inp in (task['data'].get('inputs') or []):
                if 'target' not in inp:
                    print(f'BAD INPUT   {task["id"]}.{inp.get("name")} has no "target" — a connector input '
                          f'needs {{"target": "{inp.get("name")}", "body": {{...}}}}, not "value"; as written '
                          f'the activity is dispatched without it')
                    problems.append(inp.get('name'))

# ------------------------------------------- a payload produced and never written down
#
# The Response agent drafted a claimant letter, its task went green, and no write task
# carried `claimResponseJson` into the record -- drafted, then silently discarded, with the
# case still reporting Completed. "Read by nothing" would not have caught it: the letter was
# read, by the notification's subject line. What it never reached was a Data Fabric write.
#
# Plenty of payloads legitimately never land in a column, so this is a warning and there is no
# right number of them. Do NOT count these: the test is whether each one it names is a payload
# your own block-2 data table already says has no column, and for a stated reason -- raw
# extraction, prior claims, a control-flow scalar, a value consumed only as a task input.
# **A warning naming a payload that is NOT in that table is the bug.** This comment used to say
# "on a correct plan it names three", which one correct design blew past with ten, each required
# by another rule in the seed; an agent trusting the number hunts seven phantoms or stores
# payloads it should not to silence them. Corrected 2026-08-23.
write_bodies = []
produced = set()
for node in doc['nodes']:
    for group in (node['data'].get('tasks') or []):
        for task in group:
            kind = task.get('type')
            if kind in ('process', 'rpa', 'agent'):
                for out in (task['data'].get('outputs') or []):
                    if out.get('custom') or (out.get('name') or '').endswith('Error'):
                        continue
                    # `var` is the case variable a write body reads; under the build's reassign shape
                    # `id` is the camelCased output name (outEligibilityChecksJSON) and `var` the
                    # variable (eligibilityChecksJson) -- keying on id warned on every reassigned
                    # output although each payload was written.
                    produced.add(out.get('var') or out.get('id'))
            elif kind == 'execute-connector-activity':
                for inp in (task['data'].get('inputs') or []):
                    if inp.get('target') == 'body' or inp.get('name') == 'body':
                        write_bodies.append(json.dumps(inp.get('body') or inp.get('value') or {}))

blob = ' '.join(write_bodies)
unwritten = [n for n in sorted(x for x in produced if x)
             if not re.search(r'\bvars\.' + re.escape(n) + r'\b', blob)]
if unwritten:
    print(f'WARNING  {len(unwritten)} produced variable(s) reach no write body: {", ".join(unwritten)} — '
          f'check each against your design\'s data table; one that belongs on the claim record is the bug')

# ------------------------------------------------------------- reachability: orphan stages
#
# With edges retired, an entry condition is the *only* thing that makes a stage reachable, and a
# stage without one renders exactly like a stage with one. Measured 2026-08-20: a plan whose
# terminal Denied stage had no entryConditions at all passed every gate, deployed, and parked
# with "The case manager returned no actions to execute" and every task green.
#
# One stage is *meant* to be unreachable — `pdd.md` §3 asks for an empty placeholder that must
# exist in the lifecycle and must not do anything yet. It is told apart from a real orphan by
# its tasks: a stage with work in it and no way in is a defect; a stage with neither is the
# placeholder, and it is reported as a warning so a reviewer counting them knows which is which.
first = stages[0]['id'] if stages else None
for stage in stages:
    if stage['id'] == first or (stage['data'].get('entryConditions') or []):
        continue
    label = labels.get(stage['id'])
    if any(g for g in (stage['data'].get('tasks') or []) for _ in g):
        print(f'ORPHAN      {label} has tasks and no entry condition — nothing can reach it, and '
              f'with edges retired the canvas cannot show you that')
        problems.append(stage['id'])
    else:
        print(f'WARNING  {label} has no entry condition and no tasks — expected only of the one '
              f'deliberate placeholder; say so in your design')

# --------------------------------------------------- one write per stage, and the pairing
#
# Two rules from `3d-case/cookbook.md`, *Structure* — both broken by every build measured so far.
#
# 1. One entity write per stage, as its last required task. A stage holding a human gateway
#    writes twice -- the recommendation before it opens, the decision after. Nothing writes
#    three times: measured 2026-08-23, two independent builds each wrote the letter, the
#    settlement and the closure separately in the approved ending, three round trips for
#    fields that were all known at once. 14 and 15 writes against a budget of nine.
#
# 2. A secondary stage entered on a gate decision needs a matching DIVERTING EXIT on the
#    origin. The entry rule alone is not enough: the origin's completion exit and the lane's
#    entry both fire from the same event, so either both fire or neither does. Sol1 hit the
#    deadlock on 2026-08-23 -- `Denied` completed and the case sat Running forever.

# 3. A plan that writes the record ZERO times passes every other rule here and every
#    platform gate, then reaches the validation app with an empty table. Measured
#    2026-08-26: seven stages, thirty-one tasks, not one entity write, and this script
#    said `0 referential problems`. The budget rule below only ever looked for too
#    many. Components computing the values is not the same as anything storing them.
def _is_write(t):
    """A create or update of an entity record. A Get/Query/List read is not a write (sol61,
    2026-10-30: GetEntityRecord_V3 reads were counted against the budget)."""
    d = json.dumps(t.get('data') or {})
    if re.search(r'(Create|Update|Insert|Upsert|Delete)EntityRecord', d):
        return True
    return 'EntityRecord' in d and not re.search(r'(Get|Query|List)EntityRecord', d)


_all_writes = [t for stage in stages
               for g in (stage['data'].get('tasks') or []) for t in g
               if _is_write(t)]
if stages and not _all_writes:
    print('WARNING  the plan never writes the claim record — no task anywhere carries an '
          'entity write. Every screen and every report reads that record, so a plan like '
          'this deploys, runs green and renders nothing. **This is a warning and not a '
          'failure only because a component you invoke may do the write itself** — if one '
          'does, this line is discharged; if none does, nothing is storing anything. '
          'The check that cannot be fooled is the record having rows after a run.')

for stage in stages:
    label = stage['data'].get('label', stage['id'])
    tasks = [t for g in (stage['data'].get('tasks') or []) for t in g]
    writes = [t for t in tasks if _is_write(t)]
    if not writes:
        continue
    # A human gateway is an `action` task -- the only task type a person completes. Two per
    # plan, at the two gateways. Everything else is rpa, agent, connector or timer.
    budget = 2 if any(t.get('type') == 'action' for t in tasks) else 1
    if len(writes) > budget:
        names = ', '.join(t.get('displayName') or t['id'] for t in writes)
        print(f'WARNING  {label} makes {len(writes)} entity writes (budget {budget}) — {names}. '
              f'Adjacent writes with no gateway between them are one write '
              f'(`3d-case/cookbook.md`, Structure)')

# A secondary lane entered on a gate decision, with no diverting exit anywhere, is the
# deadlock shape. Report it against the ORIGIN, which is where the missing exit belongs.
DECISION_ENTRY = ('selected-stage-completed', 'selected-stage-exited')
diverts_to = set()
for stage in stages:
    for cond in (stage['data'].get('exitConditions') or []):
        # The schema and the skill put exitToStageId on the CONDITION; an earlier build
        # put it on the RULE and this check read only that (findings 3d, 2026-08-27).
        # Read both, so a plan authored per the schema is not reported as unreachable.
        if cond.get('exitToStageId'):
            diverts_to.add(cond['exitToStageId'])
        for group in cond['rules']:
            for rule in group:
                if rule.get('exitToStageId'):
                    diverts_to.add(rule['exitToStageId'])

# A skipCondition does not stop a human gate being raised: the platform instantiates the
# Action Center task before it evaluates the skip (measured 2026-08-27, a clean claim got a
# row). The shape that works is an inverted ENTRY condition on a non-required gate, with
# the follower given its own way to start -- 3d-case/cookbook.md, Structure.
for node in doc['nodes']:
    for group in (node['data'].get('tasks') or []):
        for task in group:
            if task.get('type') == 'action' and (task.get('skipCondition') or (task.get('data') or {}).get('skipCondition')):
                name = task.get('displayName') or (task.get('data') or {}).get('displayName') or task.get('id')
                required = task.get('isRequired') or (task.get('data') or {}).get('isRequired')
                # Advisory unless the gate is also required: a non-required gate whose entry
                # condition carries the inverted test is the working shape, and a leftover
                # skipCondition on it is harmless.
                print(f"WARNING  action task {name!r} carries a skipCondition -- a skip does not stop the task being raised; "
                      f"the working shape is an inverted entry condition on a non-required gate (`3d-case/cookbook.md`, Structure)"
                      + ("" if not required else " -- and this gate IS required, so a clean claim will get a task"))
                if required:
                    problems.append(task['id'])

# The pairing is also met without a diverting exit when every other stage entered from the
# same origin is guarded by a test that cannot be true together with the lane's: the same
# variable compared to a different literal, or the same comparison inverted.
CMP = re.compile(r'vars\.(\w+)\)?(?:\.toLowerCase\(\))?\s*(===|!==)\s*("[^"]*"|true|false)')

def exclusive(a, b):
    for v, op1, l1 in CMP.findall(a or ''):
        for w, op2, l2 in CMP.findall(b or ''):
            if v == w and ((op1 == op2 == '===' and l1 != l2) or (l1 == l2 and op1 != op2)):
                return True
    return False

def entries_from(origin_id, skip):
    for st in stages:
        if st['id'] == skip:
            continue
        for cond in (st['data'].get('entryConditions') or []):
            for group in cond['rules']:
                for rule in group:
                    if rule.get('rule') in DECISION_ENTRY and origin_id in stage_refs(rule):
                        yield rule.get('conditionExpression')

for stage in stages:
    if stage['data'].get('stageType') != 'secondary' or stage['id'] in diverts_to:
        continue
    origins = []
    for cond in (stage['data'].get('entryConditions') or []):
        for group in cond['rules']:
            for rule in group:
                if rule.get('rule') in DECISION_ENTRY:
                    for src in stage_refs(rule):
                        others = list(entries_from(src, stage['id']))
                        if others and all(exclusive(rule.get('conditionExpression'), e) for e in others):
                            continue
                        origins.append(labels.get(src, src))
    if origins:
        srcs = ', '.join(sorted(set(origins)))
        print(f'WARNING  secondary {stage["data"].get("label", stage["id"])} is entered on a gate '
              f'decision from {srcs}, but no stage carries a diverting exit to it. The lane\'s '
              f'entry and the origin\'s completion fire from the same event — pair them, or the '
              f'two paths are not mutually exclusive (`3d-case/cookbook.md`, Structure)')

# ------------------------------------------- expressions must survive t=0, when nothing is set
#
# The engine evaluates EVERY entry/exit/completion condition once at case start, in an element
# called CaseRulesEvaluatorNode that appears nowhere in the plan -- and at that moment every
# variable an agent will later write is empty. An expression that throws there does not park a
# stage, it faults the whole claim. Measured 2026-08-23: 11 of 11 claims Faulted 8s after start on
# `Cannot read property 'verdict' of null`, from JSON.parse of the string "null".
#
# This is a lint, not an evaluator -- it flags the two shapes that throw on empty input. The
# ten-minute belt-and-braces check is to eval every expression in node against undefined, null,
# "" and an unparseable string before packing.

UNGUARDED_PARSE = re.compile(r'JSON\.parse\(\s*(?!.{0,80}?\|\|)[^)]*\)\s*(?:\.|\[)')
UNGUARDED_PROP  = re.compile(r'\bvars\.(\w+)\.(\w+)')

def conditions(stage):
    for scope in ('entryConditions', 'exitConditions'):
        for cond in (stage['data'].get(scope) or []):
            for group in cond['rules']:
                for rule in group:
                    expr = rule.get('conditionExpression')
                    if expr:
                        yield scope, cond, expr

for stage in stages:
    label = stage['data'].get('label', stage['id'])
    for scope, cond, expr in conditions(stage):
        why = None
        if UNGUARDED_PARSE.search(expr):
            why = 'JSON.parse(...) with no `|| \'{}\'` default, then a property read'
        else:
            m = UNGUARDED_PROP.search(expr)
            # vars.x.y is fine when x is guarded by ?. or a default somewhere in the expression
            if m and '?.' not in expr and '||' not in expr:
                why = f'reads vars.{m.group(1)}.{m.group(2)} with no `?.` and no default'
        if why:
            print(f'T-ZERO      {label}/{scope}/{cond["id"]} {why} — at case start every agent '
                  f'variable is empty and this throws, faulting the whole claim '
                  f'(`3d-case/cookbook.md`, The whole claim faults at case start)')
            problems.append(cond['id'])

# ------------------------------------------------- what `sdd convert` carries over from the SDD
#
# An expression copied with the SDD's backticks is a string, not an expression: `"`=js:…`"`
# reaches the runtime as that literal text, and the variable it feeds holds it.
def strings(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)
    elif isinstance(o, str):
        yield o
ticked = sorted({v[:60] for v in strings(doc.get('nodes', [])) if re.match(r'\s*`=(js|vars|bindings|jsonString):', v)})
for v in ticked:
    print(f'BACKTICKED  {v}… — the backticks are the SDD\'s markdown; remove them or the value is this literal text')
    problems.append(v)

# Tasks sharing one task set lose their own entryConditions when the plan compiles, and start
# with the stage (3d-case/cookbook.md, What only a run shows).
for stage in stages:
    for g in (stage['data'].get('tasks') or []):
        if len(g) > 1 and any(t.get('entryConditions') for t in g):
            names = ', '.join(t.get('displayName', t['id']) for t in g)
            print(f"WARNING  {stage['data'].get('label')}: {names} share one task set and carry entry conditions — "
                  "give each conditioned task its own set, then grep the compiled .bpmn for each rule id")

# Two entryConditions on one element are ANDed, not alternatives (3d-case/cookbook.md).
for stage in stages:
    for g in (stage['data'].get('tasks') or []):
        for t in g:
            ec = t.get('entryConditions') or []
            if len(ec) > 1:
                print(f"WARNING  {stage['data'].get('label')}/{t.get('displayName', t['id'])} has {len(ec)} entry conditions "
                      f"({', '.join(c.get('displayName', c.get('id', '?')) for c in ec)}) — they are ANDed; alternatives "
                      "are DNF groups inside one condition")

# ------------------------------------------------ file outputs: the shape the runtime accepts
#
# A `file` output reaches its case variable only through `=orchestrator.JobAttachments`.
# `sdd convert` writes `target: "=<id>"`, which faults every claim at the first file read
# (400300 `Failed to evaluate expression: =out_ClaimFormPDF`). A `body` on the one entry is
# compiled into the mapping and the variable then holds the JSON schema
# (`AGENT_STARTUP.INPUT_VALIDATION_ERROR`). Both pass `validate --strict`. A `body` is fine on
# a file entry that keeps its own variable beside a `jsonSchema` extraction of the same name.
for node in doc['nodes']:
    for group in (node['data'].get('tasks') or []):
        for task in group:
            outs = task['data'].get('outputs') or []
            for out in outs:
                if out.get('type') != 'file':
                    continue
                name = out.get('name')
                if out.get('target') != '=orchestrator.JobAttachments':
                    print(f'FILE TARGET {task.get("displayName", task["id"])}.{name} targets {out.get("target")!r} — '
                          f'a file output needs "=orchestrator.JobAttachments"; as written the claim faults at the first read')
                    problems.append(name)
                companion = any(o is not out and o.get('name') == name and o.get('type') == 'jsonSchema' for o in outs)
                if 'body' in out and not companion:
                    print(f'FILE BODY   {task.get("displayName", task["id"])}.{name} carries a body — on a single file entry '
                          f'the variable then holds the schema, not the file; remove it')
                    problems.append(name)

# ----------------------------------------- a gate opens on a record that already has the analysis
#
# The review screen reads the claim record. A stage that runs an agent or automation and then a
# human gate must write the record between them, or the reviewer opens a task with nothing to
# review (`3d-case/cookbook.md`, Structure: one write before the gate opens, one after it closes).
by_id = {}
for stage in stages:
    for g in (stage['data'].get('tasks') or []):
        for t in g:
            by_id[t['id']] = (stage, t)

def before(task, seen=None):
    """Task ids this task waits for, transitively, through `selected-tasks-completed`."""
    seen = set() if seen is None else seen
    for cond in (task.get('entryConditions') or []):
        for group in cond['rules']:
            for rule in group:
                for tid in (rule.get('selectedTasksIds') or rule.get('selectedTaskIds') or []):
                    if tid not in seen and tid in by_id:
                        seen.add(tid)
                        before(by_id[tid][1], seen)
    return seen

for tid, (stage, task) in by_id.items():
    if task.get('type') != 'action':
        continue
    prior = [by_id[p][1] for p in before(task)]
    producers = [p for p in prior if p.get('type') in ('agent', 'rpa', 'process')]
    writes = [p for p in prior if _is_write(p)]
    if producers and not writes:
        names = ', '.join(p.get('displayName', p['id']) for p in producers)
        print(f'GATE BEFORE WRITE  {stage["data"].get("label")}/{task.get("displayName", tid)} opens after {names} '
              f'with no record write between them — the reviewer sees none of that work')
        problems.append(tid)

# ------------------------------------------- a condition reading an output's id instead of its variable
#
# Where an output row's `id` differs from its `var` (the reassign shape), the id reads null in
# conditions at run time; only the variable it writes carries the value. A stage gated on the
# id never moves (`3e-run/cookbook.md`).
reassigned = {}
for node in doc['nodes']:
    for group in (node['data'].get('tasks') or []):
        for task in group:
            for out in (task['data'].get('outputs') or []):
                if out.get('id') and out.get('var') and out['id'] != out['var'] and not out.get('custom'):
                    reassigned[out['id']] = out['var']

def all_conditions():
    for stage in stages:
        for scope, cond, expr in conditions(stage):
            yield stage['data'].get('label'), expr
        for g in (stage['data'].get('tasks') or []):
            for t in g:
                for cond in (t.get('entryConditions') or []):
                    for group in cond['rules']:
                        for rule in group:
                            if rule.get('conditionExpression'):
                                yield f'{stage["data"].get("label")}/{t.get("displayName", t["id"])}', rule['conditionExpression']

for where, expr in all_conditions():
    for oid, var in reassigned.items():
        if re.search(r'\bvars\.' + re.escape(oid) + r'\b', expr) and not re.search(r'\bvars\.' + re.escape(var) + r'\b', expr):
            print(f'WARNING  {where} reads vars.{oid}, an output id written into vars.{var} — the id reads null '
                  f'at run time; test vars.{var}')

# ------------------------------------------------------------- the case's own name
if not re.fullmatch(r'ClaimCase-[A-Za-z0-9]+', doc.get('name') or ''):
    print(f'WARNING  the case is named {doc.get("name")!r} — `CONFIG.md` names it ClaimCase-<seat>; '
          f'`sdd convert` copies the whole SDD cell, notes included')

# ------------------------------------------------------------- legibility (warnings)
# Entry conditions drive execution; edges draw the picture. A plan with none runs
# correctly and renders as disconnected boxes, which is how a case becomes
# unmaintainable without ever failing.
# Edges are retired: flow lives only in the conditions, so `edges: []` is correct and an
# authored edge is the thing worth reporting. Corrected 2026-08-20 — this script warned the
# other way round for nine days, on advice that was already out of date when it was written.
if edges:
    print(f'WARNING  {len(edges)} edge(s) authored — edges are retired; flow belongs in entry '
          f'and exit conditions and `edges` should be []')

# Layout is the one purely visual thing left, and an unplaced plan is a grid in declaration order.
if stages and not layout.get('nodes'):
    print('WARNING  no layout.nodes — the canvas will auto-arrange, which reads as a wall of boxes')

print(f'{len(stages)} stages, {len(edges)} edges — {len(problems) - len(missing)} referential problem(s)')
sys.exit(1 if problems else 0)
