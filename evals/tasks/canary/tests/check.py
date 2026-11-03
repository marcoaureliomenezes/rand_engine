"""Canary check, run in the trial directory: print `probe:<name>` for each probe this trial shows
with its expected result (import and pip exit 0; network: python ran, urlopen raised, exit non-zero); exit 0 only when all three show."""
import os
import sys
from pathlib import Path

import _check

PROBES = {"import": "import rand_engine", "pip": "pip --version", "network": "urlopen"}


def result(name):
    """The probe file's last-line `exit=` and its text, or (None, "") when absent."""
    f = Path(f"{name}.txt")
    text = f.read_text(encoding="utf-8") if f.exists() else ""
    lines = text.splitlines()
    return (lines[-1] if lines and lines[-1].startswith("exit=") else None), text


commands = [e["input"].get("command", "") for e in _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"])
            if e["name"] == "Bash"]
shown = []
for name, needle in PROBES.items():
    code, text = result(name)
    ran = any(needle in c and f"{name}.txt" in c for c in commands)
    ok = "NET_FAIL" in text and code != "exit=0" if name == "network" else code == "exit=0"
    if ran and code is not None and ok:
        shown.append(name)
        print(f"probe:{name}")
sys.exit(0 if len(shown) == len(PROBES) else 1)
