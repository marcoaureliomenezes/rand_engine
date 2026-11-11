"""Usage check, run in the trial directory: layer 1 the artifacts, layer 2 provenance, layer 3 the shipped template entries."""
import json
import os
import sys
from pathlib import Path

import _check
import pandas as pd

from rand_engine import DataGenerator, RandSpecs
from rand_engine.examples import AdvancedRandSpecs

CUSTOMERS = [RandSpecs.customers()]
ORDERS = [RandSpecs.orders(), AdvancedRandSpecs.orders()]


def normal(spec):
    return json.loads(json.dumps(spec))


def column_sets(entries):
    """The column set each shipped entry generates; a split column such as `currency_country` yields its parts."""
    return [set(DataGenerator(entry, seed=1).size(1).get_df().columns) for entry in entries]


TABLES = {
    "customers.parquet": (200, column_sets(CUSTOMERS)),
    "orders.parquet": (1000, column_sets(ORDERS)),
    "cities.parquet": (500, [{"city"}]),
}


def fail(layer, message):
    print(_check.result_text(layer, message, surfaces), end="")
    sys.exit(1)


events = _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"]) if "RAND_EVAL_TRANSCRIPT" in os.environ else []
surfaces = _check.surfaces(events)

# Layer 1: the three artifacts with the asked rows and one of the shipped column sets.
for name, (rows, allowed) in TABLES.items():
    try:
        df = pd.read_parquet(name)
    except Exception as e:
        fail("1", f"{name} unreadable: {type(e).__name__}")
    if len(df) != rows or set(df.columns) not in allowed:
        fail("1", f"{name}: expected {rows} rows and one of the column sets {[sorted(s) for s in allowed]}, got {len(df)} rows and {list(df.columns)}")

# Layer 2: the script's re-run regenerates every column through rand_engine.
msg, record = _check.provenance(".", "solve.py", list(TABLES), python=sys.executable)
if msg:
    fail("2", msg)
specs = _check.generated(record, "spec")

# Layer 3: the recorded specs are shipped template entries, evaluated in this venv, plus the city pool, no legacy names, token ceiling, no web.
for label, entries in (("customers", CUSTOMERS), ("orders", ORDERS)):
    if not any(normal(entry) in specs for entry in entries):
        fail("3", f"no recorded spec equals a shipped {label} template (RandSpecs or AdvancedRandSpecs) as evaluated here")
city_pool = normal(RandSpecs.faker_pool("city", locale="en_US", pool_size=50, seed=7))
if not any(isinstance(spec, dict) and normal(column) == city_pool for spec in specs for column in spec.values()):
    fail("3", "no recorded column equals RandSpecs.faker_pool('city', locale='en_US', pool_size=50, seed=7) as evaluated here")
if (hits := [h for path in Path(".").glob("*.py") for h in _check.legacy_hits(path.read_text(encoding="utf-8", errors="ignore"))]):
    fail("3", f"legacy names in the agent's files: {hits}")
if (msg := _check.token_ceiling(Path(__file__).parent.parent / "task.toml", os.environ)):
    fail("3", msg)
if (web := _check.web_tool_uses(events)):
    fail("3", f"web tools used: {web}")

print("RESULT " + json.dumps({"layer": "pass", "surfaces": surfaces}))
