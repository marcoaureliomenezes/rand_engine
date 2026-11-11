"""Check of spark-generator, run in the trial directory with the trial venv's python (pyspark installed by task.toml).

Layer 1: `orders.parquet` is one file, or a directory of parquet parts (hidden `_` and `.` files skipped by `_check.read_artifact`), of 1,000 rows with the columns `order_id`, `order_ref`.
Layer 2: `make.py` re-runs through rand_engine's SparkGenerator and reproduces both columns.
Layer 3: the recorded spec formats a `pk`, no legacy names in the agent's .py files, no web tool, within the ceiling.
A trial that fails layer 1 and whose transcript shows Spark or Java refusing to start is a harness cause (the sandbox
blocks loopback or the Java runtime), not a documentation gap: the message says so.
"""
import os
import sys
from pathlib import Path

import _check

TASK_TOML = Path(__file__).resolve().parents[1] / "task.toml"
ARTIFACT = "orders.parquet"
HARNESS_MARKERS = ("java.net.BindException", "Cannot assign requested address", "JAVA_HOME is not set",
                   "java: command not found", "Unable to locate a Java Runtime")


def harness_hint(transcript):
    text = Path(transcript).read_text(encoding="utf-8", errors="replace") if transcript else ""
    hit = [m for m in HARNESS_MARKERS if m in text]
    return f" (harness cause: the transcript shows {hit[0]!r}, Spark could not start in the sandbox)" if hit else ""


def verdict():
    transcript = os.environ.get("RAND_EVAL_TRANSCRIPT")
    events = _check.tool_events(transcript) if transcript else []
    seen = _check.surfaces(events)
    try:
        df = _check.read_artifact(ARTIFACT)
    except Exception as e:
        return "1", f"cannot read {ARTIFACT} as a parquet file or a directory of parts: {type(e).__name__}{harness_hint(transcript)}", seen
    if len(df) != 1000 or list(df.columns) != ["order_id", "order_ref"]:
        return "1", f"{ARTIFACT} has {len(df)} rows and columns {list(df.columns)}", seen
    msg, record = _check.provenance(".", "make.py", [ARTIFACT])
    if msg:
        return "2", msg, seen
    specs = _check.generated(record, "spec")
    if not _check.documented_method(specs, "pk", ["format"]):
        return "3", "the recorded spec has no pk column with a format", seen
    hits = {name for p in Path(".").glob("*.py") for name in _check.legacy_hits(p.read_text(encoding="utf-8", errors="ignore"))}
    if hits:
        return "3", f"legacy names in the agent's code: {sorted(hits)}", seen
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
