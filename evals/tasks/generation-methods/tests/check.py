"""generation-methods check, run in the trial directory: layer 1 the artifact, layer 2 provenance, layer 3 the zipf method."""

import json
import os
import sys
from pathlib import Path

import _check
import pandas as pd

ART = "product_views.csv"


def fail(layer, message):
    sys.stdout.write(_check.result_text(layer, message, surfaces))
    sys.exit(1)


events = _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"]) if "RAND_EVAL_TRANSCRIPT" in os.environ else []
surfaces = _check.surfaces(events)

try:
    frame = pd.read_csv(ART)
    views = pd.to_numeric(frame["views"], errors="raise")
    ids = frame["product_id"]
    ok = set(frame.columns) == {"product_id", "views"} and len(frame.columns) == 2 and len(ids) == 5000 and list(ids) == list(range(1, 5001)) and (views >= 1).all() and views.max() >= 10 * views.median()
except Exception:
    ok = False
if not ok:
    fail("1", f"{ART} lacks the columns product_id and views only, 5,000 rows, sequential product_id and heavy-tailed positive views")

msg, record = _check.provenance(".", "solve.py", [ART], python=sys.executable)
if msg:
    fail("2", msg)
specs = _check.generated(record, "spec")

if not any(isinstance(c, dict) and c.get("method") == "zipf" and isinstance(c.get("kwargs"), dict) and c["kwargs"].get("a") == 1.5
           for spec in specs if isinstance(spec, dict) for c in spec.values()):
    fail("3", "the recorded spec holds no zipf column with kwargs a=1.5")
if hits := [h for p in Path(".").glob("*.py") for h in _check.legacy_hits(p.read_text(encoding="utf-8", errors="ignore"))]:
    fail("3", f"legacy syntax: {sorted(set(hits))}")
if msg := _check.token_ceiling(Path(__file__).parent.parent / "task.toml", os.environ):
    fail("3", msg)
if web := _check.web_tool_uses(events):
    fail("3", f"web tools used: {web}")
print("RESULT " + json.dumps({"layer": "pass", "surfaces": surfaces}))
