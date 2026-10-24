#!/usr/bin/env python3
"""Save the inputs a case instance actually sent one of its Agents, so a fix is proven on them.

  python3 4-verify/agent_inputs.py --deploy-folder-key <key of ClaimCase-<seat>-Deploy> \\
      --agent DecisionRecommendation --instance <case instance id> --out agent-inputs.json

Then `uip agent debug Build/ClaimCase-<seat>/<Agent> --inputs "$(cat agent-inputs.json)"` reruns the
Agent on exactly what the case gave it. Run it from inside your seat folder. Agent jobs run in the
deploy folder, not the seat folder. This pages at 50.
"""
import argparse, json, subprocess, sys


def uip(*args):
    out = subprocess.run(["uip", *args, "--output", "json"], capture_output=True, text=True).stdout
    return json.loads(out or "{}")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--deploy-folder-key", required=True)
    p.add_argument("--agent", required=True, help="the Agent's process name, or part of it")
    p.add_argument("--instance", required=True, help="the case instance id (the JobKey `case process run` returned)")
    p.add_argument("--out", required=True)
    p.add_argument("--created-after", help="ISO time, to narrow the search")
    a = p.parse_args()

    found, offset = None, 0
    while found is None:
        q = ["or", "jobs", "list", "--folder-key", a.deploy_folder_key, "--process-name", a.agent,
             "--all-fields", "--limit", "50", "--offset", str(offset)]
        if a.created_after:
            q += ["--created-after", a.created_after]
        jobs = uip(*q).get("Data") or []
        found = next((j for j in jobs if a.instance.lower() in json.dumps(j).lower()), None)
        if found is None and len(jobs) < 50:
            sys.exit(f"no {a.agent} job found for instance {a.instance} in that folder")
        offset += 50

    job = uip("or", "jobs", "get", found["Key"]).get("Data") or {}
    args = job.get("InputArguments")
    args = json.loads(args) if isinstance(args, str) else args   # a JSON string inside the JSON
    with open(a.out, "w") as fh:
        json.dump(args, fh, indent=1)
    print(f"job {found['Key']}: {len(args or {})} inputs saved to {a.out}")


if __name__ == "__main__":
    main()
