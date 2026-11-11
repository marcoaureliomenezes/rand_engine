"""Writers-and-streaming check, run in the trial directory.
Layer 1: customers.csv.gz holds 1000 rows of age, country, amount; stream_out holds part files with those columns.
Layer 2: the batch file's columns match what a re-run of solve.py generated through rand_engine (the stream is time-bound: no provenance).
Layer 3: the recorded spec uses the integers method, the re-run actually called a batch writer's save() and a stream writer's start() (recorded by `_check.provenance`), no legacy names, no web use, within the ceiling."""
import os
import sys
from pathlib import Path

import _check

COLS = ["age", "country", "amount"]
BATCH, SINK, SCRIPT = "customers.csv.gz", "stream_out", "solve.py"


def run(events):
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
    msg, record = _check.provenance(".", SCRIPT, [BATCH])
    if msg:
        return "2", msg
    specs, calls = _check.generated(record, "spec"), _check.generated(record, "entry")
    if not _check.documented_method(specs, "integers", ["min", "max"]):
        return "3", "the recorded spec has no integers column with min and max"
    if not {"save", "start"} <= set(calls):
        return "3", f"the script did not write through rand-engine's file writers (writer calls that ran: {sorted(set(calls))}): expected the batch writer's save() and the stream writer's start(), not pandas I/O"
    if (hits := {h for p in Path(".").glob("*.py") for h in _check.legacy_hits(p.read_text(encoding="utf-8", errors="ignore"))}):
        return "3", f"legacy names in the agent's code: {sorted(hits)}"
    if _check.web_tool_uses(events):
        return "3", "the agent used a web tool"
    if (msg := _check.token_ceiling(Path(__file__).parent.parent / "task.toml", os.environ)):
        return "3", msg
    return None, None


transcript = os.environ.get("RAND_EVAL_TRANSCRIPT")
events = _check.tool_events(transcript) if transcript else []
seen = _check.surfaces(events)
layer, out = run(events)
if layer:
    print(_check.result_text(layer, out, seen), end="")
    sys.exit(1)
print("RESULT " + __import__("json").dumps({"layer": "pass", "surfaces": seen}))
