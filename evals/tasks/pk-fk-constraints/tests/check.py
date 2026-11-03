"""pk-fk-constraints check, run in the trial directory by `evals/run.py`: exit 0 when all three layers pass.

Layer 1: customers.parquet (1000 rows) and orders.parquet (5000 rows) with every order's customer_id a customer.
Layer 2: solve.py re-runs and rand_engine generated every column. Layer 3: the recorded specs hold a pk column and
an fk column whose parent is that pk dict and parent_size is the parent's rows; no legacy syntax, no web tool, within the ceiling.
"""
import json
import os
import sys
from pathlib import Path

import _check
import pandas as pd

work, specs = Path.cwd(), []
env = os.environ


def fail(layer, message, surfaces=()):
    print(_check.result_text(layer, message, surfaces), end="")
    sys.exit(1)


try:
    customers, orders = pd.read_parquet("customers.parquet"), pd.read_parquet("orders.parquet")
    ok = (len(customers), len(orders)) == (1000, 5000) and bool(orders["customer_id"].isin(customers["customer_id"]).all())
except Exception as e:
    fail("1", f"cannot read the tables: {type(e).__name__}")
if not ok:
    fail("1", "the tables lack the asked rows or an order references no customer")

events = _check.tool_events(env["RAND_EVAL_TRANSCRIPT"]) if "RAND_EVAL_TRANSCRIPT" in env else []
surfaces = _check.surfaces(events)

problem = _check.provenance(work, "solve.py", ["customers.parquet", "orders.parquet"], python=sys.executable, specs=specs)
if problem:
    fail("2", problem, surfaces)

pks = [e for s in specs if isinstance(s, dict) for e in s.values() if isinstance(e, dict) and e.get("method") == "pk"]
fks = [e.get("kwargs", {}) for s in specs if isinstance(s, dict) for e in s.values() if isinstance(e, dict) and e.get("method") == "fk"]
legacy = [h for p in work.glob("*.py") for h in _check.legacy_hits(p.read_text(encoding="utf-8"))]
if not any(k.get("parent") in pks and k.get("parent_size") == len(customers) for k in fks):
    fail("3", "no fk column whose parent is a pk dict and parent_size is the customers' rows", surfaces)
if legacy:
    fail("3", f"legacy syntax: {legacy}", surfaces)
if _check.web_tool_uses(events):
    fail("3", "the agent used a web tool", surfaces)
ceiling = _check.token_ceiling(Path(__file__).resolve().parent.parent / "task.toml", env)
if ceiling:
    fail("3", ceiling, surfaces)
print(f"RESULT {json.dumps({'layer': 'pass', 'surfaces': surfaces})}")
