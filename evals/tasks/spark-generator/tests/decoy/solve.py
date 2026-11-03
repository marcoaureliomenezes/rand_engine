"""Decoy: the same orders from pandas alone, no rand_engine."""
import subprocess
import sys
from pathlib import Path

Path("make.py").write_text('''import pandas as pd

ids = range(1, 1001)
pd.DataFrame({"order_id": list(ids), "order_ref": [f"ORD-{i:06d}" for i in ids]}).to_parquet("orders.parquet", index=False)
''')
subprocess.run([sys.executable, "make.py"], check=True)
