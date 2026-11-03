"""Check of get-started-cli, run in the trial directory with the trial venv's python.

Layer 1: `starter/lake-example.py` exists. Layer 2: it is byte-equal to the packaged `cases/lake.py.txt` and,
when the transcript is given, a Bash call ran `rand-engine get-started lake --out`. Layer 3: no web tool, within the ceiling.
"""
import os
import sys
from importlib import resources
from pathlib import Path

import _check

TASK_TOML = Path(__file__).resolve().parents[1] / "task.toml"
SCAFFOLD = Path("starter") / "lake-example.py"


def verdict():
    if not SCAFFOLD.is_file():
        return "layer1", f"{SCAFFOLD} does not exist", ()
    packaged = (resources.files("rand_engine") / "cases" / "lake.py.txt").read_bytes()
    if SCAFFOLD.read_bytes() != packaged:
        return "layer2", f"{SCAFFOLD} is not byte-equal to the packaged cases/lake.py.txt", ()
    transcript = os.environ.get("RAND_EVAL_TRANSCRIPT")
    events = _check.tool_events(transcript) if transcript else []
    if transcript and not any(e["name"] == "Bash" and "rand-engine" in (c := e["input"].get("command", ""))
                              and "get-started lake" in c and "--out" in c for e in events):
        return "layer2", "the transcript shows no `rand-engine get-started lake --out` call", ()
    seen = _check.surfaces(events)
    if web := _check.web_tool_uses(events):
        return "layer3", f"web tools used: {web}", seen
    if msg := _check.token_ceiling(TASK_TOML, os.environ):
        return "layer3", msg, seen
    return None, None, seen


layer, message, seen = verdict()
if layer:
    sys.stdout.write(_check.result_text(layer, message, seen))
    sys.exit(1)
print(f"RESULT {_check.json.dumps({'layer': 'pass', 'surfaces': seen})}")
