"""Canary check, run in the trial directory: print `probe:<name>` for each probe this trial shows
with its expected result (import and pip exit 0, network exit non-zero); exit 0 only when all three show."""
import os
import sys
from pathlib import Path

import _check

PROBES = {"import": "import rand_engine", "pip": "pip --version", "network": "urlopen"}


def exit_code(name):
    f = Path(f"{name}.txt")
    lines = f.read_text(encoding="utf-8").splitlines() if f.exists() else []
    return lines[-1] if lines and lines[-1].startswith("exit=") else None


commands = [e["input"].get("command", "") for e in _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"])
            if e["name"] == "Bash"]
shown = []
for name, needle in PROBES.items():
    code = exit_code(name)
    ran = any(needle in c and f"{name}.txt" in c for c in commands)
    if ran and code is not None and (code != "exit=0") == (name == "network"):
        shown.append(name)
        print(f"probe:{name}")
sys.exit(0 if len(shown) == len(PROBES) else 1)
