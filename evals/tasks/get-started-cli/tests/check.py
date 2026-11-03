"""Check of get-started-cli, run in the trial directory with the trial venv's python.

Layer 1: `starter/lake-example.py` exists. Layer 2: it is byte-equal to the packaged `cases/lake.py.txt` and,
when the transcript is given, a Bash call ran the package CLI's `get-started`, in any option order. Layer 3: no web tool,
within the ceiling.
"""
import os
import re
import sys
from importlib import resources
from pathlib import Path

import _check

TASK_TOML = Path(__file__).resolve().parents[1] / "task.toml"
SCAFFOLD = Path("starter") / "lake-example.py"
GET_STARTED = re.compile(r"\brand[-_]engine\b.*\bget-started\b")


def verdict():
    transcript = os.environ.get("RAND_EVAL_TRANSCRIPT")
    events = _check.tool_events(transcript) if transcript else []
    seen = _check.surfaces(events)
    if not SCAFFOLD.is_file():
        return "1", f"{SCAFFOLD} does not exist", seen
    packaged = (resources.files("rand_engine") / "cases" / "lake.py.txt").read_bytes()
    if SCAFFOLD.read_bytes() != packaged:
        return "2", f"{SCAFFOLD} is not byte-equal to the packaged cases/lake.py.txt", seen
    if transcript and not any(e["name"] == "Bash" and GET_STARTED.search(e["input"].get("command", ""))
                              for e in events):
        return "2", "the transcript shows no Bash call of the package CLI's get-started", seen
    if web := _check.web_tool_uses(events):
        return "3", f"web tools used: {web}", seen
    if msg := _check.token_ceiling(TASK_TOML, os.environ):
        return "3", msg, seen
    return None, None, seen


layer, message, seen = verdict()
if layer:
    sys.stdout.write(_check.result_text(layer, message, seen))
    sys.exit(1)
print(f"RESULT {_check.json.dumps({'layer': 'pass', 'surfaces': seen})}")
