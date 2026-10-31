"""E2 check, run in the trial directory: exit 0 when customers.parquet has 1000 rows,
orders.parquet 5000, and every orders.customer_id is in customers.customer_id."""

import sys

import pandas as pd

try:
    c = pd.read_parquet("customers.parquet")
    o = pd.read_parquet("orders.parquet")
    ok = (
        len(c) == 1000
        and len(o) == 5000
        and c["customer_id"].is_unique
        and bool(o["customer_id"].isin(c["customer_id"]).all())
    )
    print(f"customers={len(c)} orders={len(o)}")
except Exception as e:
    ok = False
    print(f"{type(e).__name__}: {str(e)[:200]}")
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
