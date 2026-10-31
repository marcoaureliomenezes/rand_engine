"""E3 check, run in the trial directory: exit 0 when the fixed spec.py generates 1000 rows
with columns id, name, amount, status, else exit 1."""

import importlib.util
import sys

COLUMNS = ["id", "name", "amount", "status"]

try:
    from rand_engine import DataGenerator

    sys.dont_write_bytecode = True
    s = importlib.util.spec_from_file_location("spec", "spec.py")
    mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    df = DataGenerator(mod.spec, seed=1).size(1000).get_df()
    ok = len(df) == 1000 and list(df.columns) == COLUMNS
    print(f"rows={len(df)} columns={list(df.columns)}")
except Exception as e:
    ok = False
    print(f"{type(e).__name__}: {str(e)[:200]}")
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
