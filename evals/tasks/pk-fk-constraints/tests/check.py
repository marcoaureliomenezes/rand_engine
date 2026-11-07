"""pk-fk-constraints check, run in the trial directory by `evals/run.py`: exit 0 when all three layers pass.

Layer 1: customers.parquet (1000 rows) and orders.parquet (5000 rows), exact column sets, unique keys, every order's customer_id a customer.
Layer 2: solve.py re-runs and rand_engine generated every column. Layer 3: the recorded orders customer_id is an fk whose
parent is the customers customer_id pk dict and parent_size is the customer rows; no legacy syntax, no web tool, within the ceiling.
"""
import json
import os
import sys
from pathlib import Path

import _check
import pandas as pd

work = Path.cwd()
env = os.environ


def fail(layer, message, surfaces=()):
    print(_check.result_text(layer, message, surfaces), end="")
    sys.exit(1)


events = _check.tool_events(env["RAND_EVAL_TRANSCRIPT"]) if "RAND_EVAL_TRANSCRIPT" in env else []
surfaces = _check.surfaces(events)

try:
    customers, orders = pd.read_parquet("customers.parquet"), pd.read_parquet("orders.parquet")
except Exception as e:
    fail("1", f"cannot read the tables: {type(e).__name__}", surfaces)
if set(customers.columns) != {"customer_id"} or set(orders.columns) != {"order_id", "customer_id"}:
    fail("1", f"expected columns customer_id and order_id, customer_id; got {list(customers.columns)} and {list(orders.columns)}", surfaces)
if (len(customers), len(orders)) != (1000, 5000) or not orders["customer_id"].isin(customers["customer_id"]).all():
    fail("1", "the tables lack the asked rows or an order references no customer", surfaces)
if not (customers["customer_id"].is_unique and orders["order_id"].is_unique):
    fail("1", "customers.customer_id or orders.order_id is not unique", surfaces)

problem, record = _check.provenance(work, "solve.py", ["customers.parquet", "orders.parquet"], python=sys.executable)
if problem:
    fail("2", problem, surfaces)
specs = _check.agent(record, "spec")

def col(spec, name, method):
    c = spec.get(name) if isinstance(spec, dict) else None
    return c if isinstance(c, dict) and c.get("method") == method else None


legacy = [h for p in work.glob("*.py") for h in _check.legacy_hits(p.read_text(encoding="utf-8"))]
linked = any((pk := col(c, "customer_id", "pk")) and (fk := col(o, "customer_id", "fk"))
             and isinstance(fk.get("kwargs"), dict) and fk["kwargs"].get("parent") == pk
             and fk["kwargs"].get("parent_size") == len(customers) for c in specs for o in specs)
if not linked:
    fail("3", "no orders customer_id fk whose parent is the customers customer_id pk and parent_size the customers' rows", surfaces)
if legacy:
    fail("3", f"legacy syntax: {legacy}", surfaces)
if _check.web_tool_uses(events):
    fail("3", "the agent used a web tool", surfaces)
ceiling = _check.token_ceiling(Path(__file__).resolve().parent.parent / "task.toml", env)
if ceiling:
    fail("3", ceiling, surfaces)
print(f"RESULT {json.dumps({'layer': 'pass', 'surfaces': surfaces})}")
