"""Writers-and-streaming check, run in the trial directory.
Layer 1: customers.csv.gz holds 1000 rows of age, country, amount; stream_out holds part files with those columns.
Layer 2: the batch file's columns match what a re-run of solve.py generated through rand_engine (the stream is time-bound: no provenance).
Layer 3: the recorded spec uses the integers method, the agent's code calls write...save and writeStream, no legacy names, no web use, within the ceiling."""
import os
import re
import sys
from pathlib import Path

import _check

COLS = ["age", "country", "amount"]
BATCH, SINK, SCRIPT = "customers.csv.gz", "stream_out", "solve.py"


def run():
    try:
        batch = _check.read_artifact(BATCH)
        parts = [p for p in Path(SINK).iterdir() if p.is_file()]
        stream = _check.read_artifact(SINK) if parts else None
    except Exception as e:
        return "1", f"cannot read the deliverables: {type(e).__name__}"
    if list(batch.columns) != COLS or len(batch) != 1000:
        return "1", f"{BATCH} has columns {list(batch.columns)} and {len(batch)} rows, not {COLS} and 1000"
    if stream is None or list(stream.columns) != COLS:
        return "1", f"{SINK} holds no part file with the columns {COLS}"
    specs = []
    if (msg := _check.provenance(".", SCRIPT, [BATCH], specs=specs)):
        return "2", msg
    if not _check.documented_method(specs, "integers", ["min", "max"]):
        return "3", "the recorded spec has no integers column with min and max"
    py = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in Path(".").rglob("*.py")
                   if "site-packages" not in p.parts and ".venv" not in p.parts)
    if not (re.search(r"\.write\b[\s\S]*?\.save\(", py) and re.search(r"\.writeStream\b", py)):
        return "3", "the agent's code has no write...save call and a writeStream call"
    if (hits := _check.legacy_hits(py)):
        return "3", f"legacy names in the agent's code: {hits}"
    events = _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"]) if os.environ.get("RAND_EVAL_TRANSCRIPT") else []
    if _check.web_tool_uses(events):
        return "3", "the agent used a web tool"
    if (msg := _check.token_ceiling(Path(__file__).parent.parent / "task.toml", os.environ)):
        return "3", msg
    return None, events


layer, out = run()
if layer:
    print(_check.result_text(layer, out), end="")
    sys.exit(1)
print("RESULT " + __import__("json").dumps({"layer": "pass", "surfaces": _check.surfaces(out)}))
