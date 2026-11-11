"""Check of rand-spec-grammar, run in the trial directory with the trial venv's python.

Layer 1: `out.parquet` holds 1,000 rows and the columns id, name, amount, status. Layer 2: a re-run of `make.py`
regenerates it through rand_engine. Layer 3: the recorded spec has an `integers` column, the agent's .py files use no
legacy name, no web tool, within the ceiling.
"""
import os
import sys
from pathlib import Path

import _check

TASK_TOML = Path(__file__).resolve().parents[1] / "task.toml"
COLUMNS = ["id", "name", "amount", "status"]


def verdict():
    transcript = os.environ.get("RAND_EVAL_TRANSCRIPT")
    events = _check.tool_events(transcript) if transcript else []
    seen = _check.surfaces(events)
    try:
        df = _check.read_artifact("out.parquet")
    except Exception as e:
        return "1", f"cannot read out.parquet: {type(e).__name__}", seen
    if len(df) != 1000 or list(df.columns) != COLUMNS:
        return "1", f"out.parquet has {len(df)} rows and columns {list(df.columns)}, expected 1000 rows and {COLUMNS}", seen
    if not Path("make.py").is_file():
        return "2", "make.py does not exist", seen
    msg, record = _check.provenance(".", "make.py", ["out.parquet"])
    if msg:
        return "2", msg, seen
    specs = _check.generated(record, "spec")
    if not _check.documented_method(specs, "integers", ["min", "max"]):
        return "3", "the recorded spec has no `integers` column with min and max", seen
    if hits := _check.legacy_hits("\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in Path(".").glob("*.py"))):
        return "3", f"legacy names used: {hits}", seen
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
