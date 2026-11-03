"""Usage check, run in the trial directory: layer 1 the artifacts, layer 2 provenance, layer 3 the named RandSpecs entries."""
import json
import os
import sys
from pathlib import Path

import _check
import pandas as pd

TABLES = {
    "customers.parquet": (200, ["customer_id", "age", "city", "total_spent", "is_premium", "registration_date"]),
    "orders.parquet": (1000, ["order_id", "customer_id", "amount", "order_timestamp", "status", "payment_method"]),
}
specs = []


def fail(layer, message):
    print(_check.result_text(layer, message, surfaces), end="")
    sys.exit(1)


events = _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"]) if "RAND_EVAL_TRANSCRIPT" in os.environ else []
surfaces = _check.surfaces(events)

# Layer 1: both artifacts with the asked rows and columns.
for name, (rows, columns) in TABLES.items():
    try:
        df = pd.read_parquet(name)
    except Exception as e:
        fail("1", f"{name} unreadable: {type(e).__name__}")
    if len(df) != rows or list(df.columns) != columns:
        fail("1", f"{name}: expected {rows} rows and columns {columns}, got {len(df)} rows and {list(df.columns)}")

# Layer 2: the script's re-run regenerates every column through rand_engine.
if (msg := _check.provenance(".", "solve.py", list(TABLES), python=sys.executable, specs=specs)):
    fail("2", msg)

# Layer 3: the recorded specs are the named RandSpecs entries, evaluated in this venv, plus no legacy names, token ceiling, no web.
from rand_engine import RandSpecs  # noqa: E402  (rand-engine is installed in the trial venv)


def normal(spec):
    return json.loads(json.dumps(spec))


for label, entry in (("customers", RandSpecs.customers()), ("orders", RandSpecs.orders())):
    if normal(entry) not in specs:
        fail("3", f"no recorded spec equals RandSpecs.{label}() as evaluated here")
if (hits := [h for path in Path(".").glob("*.py") for h in _check.legacy_hits(path.read_text(encoding="utf-8"))]):
    fail("3", f"legacy names in the agent's files: {hits}")
if (msg := _check.token_ceiling(Path(__file__).parent.parent / "task.toml", os.environ)):
    fail("3", msg)
if (web := _check.web_tool_uses(events)):
    fail("3", f"web tools used: {web}")

print("PASS")
print("RESULT " + json.dumps({"surfaces": surfaces}))
