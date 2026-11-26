import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

groups = json.loads(os.environ["GROUPS"])
backend = f"-backend-config={Path('terraform/backend.hcl').resolve()}"
if os.environ["GITHUB_EVENT_NAME"] == "push":
    action = ["apply", "-auto-approve", "-lock-timeout=10m", "-input=false"]
else:
    action = ["plan", "-lock=false", "-input=false"]


def commands(unit):
    key = unit.removeprefix("terraform/") + "/terraform.tfstate"
    return [
        ["fmt", "-check"],
        ["init", "-input=false", backend, f"-backend-config=key={key}"],
        ["validate"],
        action,
    ]


def run(group):
    results, blocker = [], None
    for unit in group["dirs"].split():
        if blocker:
            results.append((unit, f"skipped because {blocker} failed\n", None))
            continue
        output, ok = "", True
        for args in commands(unit):
            done = subprocess.run(["terraform", f"-chdir={unit}", *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            output += done.stdout
            if done.returncode != 0:
                ok = False
                break
        results.append((unit, output, ok))
        if not ok:
            blocker = unit
    return results


failed = False
with ThreadPoolExecutor(max_workers=max(len(groups), 1)) as pool:
    for results in pool.map(run, groups):
        for unit, output, ok in results:
            print(f"::group::{unit}")
            print(output, end="")
            print("::endgroup::")
            if ok is False:
                print(f"::error::{unit} failed")
                failed = True
            elif ok is None:
                print(f"::warning::{unit} skipped")
        sys.stdout.flush()

sys.exit(1 if failed else 0)
