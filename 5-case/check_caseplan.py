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

declared = set()
for node in doc['nodes']:
    for group in (node['data'].get('tasks') or []):
        for task in group:
            for out in (task['data'].get('outputs') or []):
                declared.add(out.get('var') or out.get('id'))

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
                    for ref in (rule.get('selectedStageIds') or []):
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
                for src in (rule.get('selectedStageIds') or []):
                    if marks_complete.get(src):
                        print(f'UNREACHABLE {labels.get(stage["id"])} enters on exited({labels.get(src, src)}), '
                              f'but that stage marks itself COMPLETE — the rule never fires')
                        problems.append(cond['id'])

# ------------------------------------------------------------- legibility (warnings)
# Entry conditions drive execution; edges draw the picture. A plan with none runs
# correctly and renders as disconnected boxes, which is how a case becomes
# unmaintainable without ever failing.
if stages and not edges:
    print('WARNING  no edges — this plan will run, and will render as disconnected boxes')
else:
    linked = set()
    for e in edges:
        linked.add((e.get('source'), e.get('target')))
    for stage in stages:
        for cond in (stage['data'].get('entryConditions') or []):
            for group in cond['rules']:
                for rule in group:
                    for src in (rule.get('selectedStageIds') or []):
                        if (src, stage['id']) not in linked:
                            print(f'WARNING  {labels.get(src, src)} -> {labels.get(stage["id"])} '
                                  f'is a real transition with no edge drawn')

print(f'{len(stages)} stages, {len(edges)} edges — {len(problems) - len(missing)} referential problem(s)')
sys.exit(1 if problems else 0)
