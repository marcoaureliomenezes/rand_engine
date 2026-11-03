"""Check of spark-generator, run in the trial directory with the trial venv's python (pyspark installed by task.toml).

Layer 1: `orders.parquet` is one file, or a directory of `part-*.parquet` files (`_SUCCESS` and `.crc` ignored), of 1,000 rows with the columns `order_id`, `order_ref`.
Layer 2: `make.py` re-runs through rand_engine's SparkGenerator and reproduces both columns.
Layer 3: the recorded spec formats a `pk`, no legacy names in the agent's .py files, no web tool, within the ceiling.
A trial that fails layer 1 and whose transcript shows Spark or Java refusing to start is a harness cause (the sandbox
blocks loopback or the Java runtime), not a documentation gap: the message says so.
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd

import _check

TASK_TOML = Path(__file__).resolve().parents[1] / "task.toml"
ARTIFACT = "orders.parquet"
HARNESS_MARKERS = ("java.net.BindException", "Cannot assign requested address", "JAVA_HOME is not set",
                   "java: command not found", "Unable to locate a Java Runtime")


def harness_hint(transcript):
    text = Path(transcript).read_text(encoding="utf-8", errors="replace") if transcript else ""
    hit = [m for m in HARNESS_MARKERS if m in text]
    return f" (harness cause: the transcript shows {hit[0]!r}, Spark could not start in the sandbox)" if hit else ""


def read_orders():
    """DataFrame of ARTIFACT, a parquet file or the part-*.parquet files of a directory; None when it is neither."""
    path = Path(ARTIFACT)
    if path.is_file():
        return pd.read_parquet(path)
    parts = sorted(path.glob("part-*.parquet")) if path.is_dir() else []
    return pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True) if parts else None


def verdict():
    transcript = os.environ.get("RAND_EVAL_TRANSCRIPT")
    events = _check.tool_events(transcript) if transcript else []
    seen = _check.surfaces(events)
    df = read_orders()
    if df is None:
        return "1", f"{ARTIFACT} is neither a parquet file nor a directory of part-*.parquet files{harness_hint(transcript)}", seen
    if len(df) != 1000 or list(df.columns) != ["order_id", "order_ref"]:
        return "1", f"{ARTIFACT} has {len(df)} rows and columns {list(df.columns)}", seen
    specs = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "work"
        shutil.copytree(".", work, ignore=shutil.ignore_patterns(ARTIFACT))
        df.to_parquet(work / ARTIFACT, index=False)
        msg = _check.provenance(work, "make.py", [ARTIFACT], specs=specs)
    if msg:
        return "2", msg, seen
    if not _check.documented_method(specs, "pk", ["format"]):
        return "3", "the recorded spec has no pk column with a format", seen
    hits = {name for p in Path(".").glob("*.py") for name in _check.legacy_hits(p.read_text(encoding="utf-8"))}
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
