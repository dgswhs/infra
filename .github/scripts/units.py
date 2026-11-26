import json
import re
import subprocess
from graphlib import TopologicalSorter
from pathlib import Path

SHARED = {".github/workflows/terraform.yml", ".github/scripts/units.py", ".github/scripts/run.py", "mise.toml", "mise.lock"}

units = sorted(str(p.parent) for p in Path("terraform").rglob("backend.tf") if ".terraform" not in p.parts)
keys = {u.removeprefix("terraform/") + "/terraform.tfstate": u for u in units}
reads = {
    u: {keys[k] for f in Path(u).glob("*.tf") for k in re.findall(r'"([^"]+/terraform\.tfstate)"', f.read_text()) if k in keys}
    for u in units
}
readers = {u: {r for r in units if u in reads[r]} for u in units}


def unit_of(path):
    return next((u for u in units if path.startswith(u + "/")), None)


changed = subprocess.run(["git", "diff", "--name-only", "HEAD^", "HEAD"], capture_output=True, text=True, check=True).stdout.split()
if any(f in SHARED or (f.startswith("terraform/") and not unit_of(f)) for f in changed):
    affected = set(units)
else:
    affected = {unit_of(f) for f in changed} - {None}

stack = list(affected)
while stack:
    for r in readers[stack.pop()] - affected:
        affected.add(r)
        stack.append(r)

groups, seen = [], set()
for u in sorted(affected):
    if u in seen:
        continue
    group, stack = set(), [u]
    while stack:
        v = stack.pop()
        if v not in group:
            group.add(v)
            stack += (reads[v] | readers[v]) & affected
    seen |= group
    order = list(TopologicalSorter({v: sorted(reads[v] & group) for v in sorted(group)}).static_order())
    groups.append({"name": ", ".join(d.removeprefix("terraform/") for d in order), "dirs": " ".join(order)})

print(f"groups={json.dumps(groups)}")
