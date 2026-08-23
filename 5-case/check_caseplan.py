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

`uip maestro case validate` refuses a Studio-Web-authored plan entirely — it expects schema
version 27.0.0 where the designer writes 30.0.0 — so this script is the only structural gate
that runs at all. Run it after every edit and before every pack.

    python3 check_caseplan.py "<path to caseplan.json>"
"""
import json, re, sys

path = sys.argv[1] if len(sys.argv) > 1 else 'caseplan.json'
doc = json.load(open(path))
problems = []


def stage_refs(rule):
    """Stage ids a rule names — under BOTH spellings, which are a schema generation apart.

    Schema 23.0.0 (what `uip maestro case` generates, and what you are building) writes
    `selectedStageId`, a single string. Schema 30.0.0 (what Studio Web writes) writes
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
                # Both, not one or the other. `var` is the display name and `id` is what
                # `=vars.X` resolves against, and they diverge whenever two tasks write the
                # same payload -- the second gets a suffixed id and keeps the shared var.
                # Preferring `var` reported that suffixed id as undeclared (a false alarm) and,
                # worse, hid a systematic id-casing bug that cost a build a deploy cycle.
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

# A rule may only name tasks that live in its own stage.
for stage in stages:
    label = stage['data'].get('label', stage['id'])
    own = {t['id'] for g in (stage['data'].get('tasks') or []) for t in g}
    for scope in ('entryConditions', 'exitConditions'):
        for cond in (stage['data'].get(scope) or []):
            for group in cond['rules']:
                for rule in group:
                    for ref in (rule.get('selectedTasksIds') or []):
                        if ref not in own:
                            print(f'BAD REF     {label}/{scope}/{cond["id"]} names task {ref}, which is not in this stage')
                            problems.append(ref)
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
# Awaiting Assessment poll loop) is *only* reachable via `exited`.

marks_complete = {
    s['id']: any(c.get('marksStageComplete') for c in (s['data'].get('exitConditions') or []))
    for s in stages
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
                    produced.add(out.get('id') or out.get('var'))
            elif kind == 'execute-connector-activity':
                for inp in (task['data'].get('inputs') or []):
                    if inp.get('target') == 'body' or inp.get('name') == 'body':
                        write_bodies.append(json.dumps(inp.get('body') or inp.get('value') or {}))

blob = ' '.join(write_bodies)
for name in sorted(n for n in produced if n):
    if not re.search(r'\bvars\.' + re.escape(name) + r'\b', blob):
        print(f'WARNING  vars.{name} is produced but reaches no write body — if it belongs on '
              f'the claim record, nothing is carrying it there')

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
# Two rules from `5-case/spec.md`, both broken by every build measured so far.
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

for stage in stages:
    label = stage['data'].get('label', stage['id'])
    tasks = [t for g in (stage['data'].get('tasks') or []) for t in g]
    writes = [t for t in tasks if 'EntityRecord' in json.dumps(t.get('data') or {})]
    if not writes:
        continue
    # A human gateway is an `action` task -- the only task type a person completes. Two per
    # plan, at the two gateways. Everything else is rpa, agent, connector or timer.
    budget = 2 if any(t.get('type') == 'action' for t in tasks) else 1
    if len(writes) > budget:
        names = ', '.join(t.get('displayName') or t['id'] for t in writes)
        print(f'WARNING  {label} makes {len(writes)} entity writes (budget {budget}) — {names}. '
              f'Adjacent writes with no gateway between them are one write '
              f'(`5-case/spec.md`, How many writes)')

# A secondary lane entered on a gate decision, with no diverting exit anywhere, is the
# deadlock shape. Report it against the ORIGIN, which is where the missing exit belongs.
DECISION_ENTRY = ('selected-stage-completed', 'selected-stage-exited')
diverts_to = set()
for stage in stages:
    for cond in (stage['data'].get('exitConditions') or []):
        for group in cond['rules']:
            for rule in group:
                if rule.get('exitToStageId'):
                    diverts_to.add(rule['exitToStageId'])

for stage in stages:
    if stage['data'].get('stageType') != 'secondary' or stage['id'] in diverts_to:
        continue
    origins = []
    for cond in (stage['data'].get('entryConditions') or []):
        for group in cond['rules']:
            for rule in group:
                if rule.get('rule') in DECISION_ENTRY:
                    origins += [labels.get(x, x) for x in stage_refs(rule)]
    if origins:
        srcs = ', '.join(sorted(set(origins)))
        print(f'WARNING  secondary {stage["data"].get("label", stage["id"])} is entered on a gate '
              f'decision from {srcs}, but no stage carries a diverting exit to it. The lane\'s '
              f'entry and the origin\'s completion fire from the same event — pair them, or the '
              f'two paths are not mutually exclusive (`5-case/spec.md`, Entering a secondary lane)')

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
