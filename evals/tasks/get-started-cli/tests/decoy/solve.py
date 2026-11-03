"""Decoy: a hand-written scaffold, no CLI."""
from pathlib import Path

Path("starter").mkdir(exist_ok=True)
Path("starter/lake-example.py").write_text(
    "import pandas as pd\n\ncustomers = pd.DataFrame({'id': range(10)})\ncustomers.to_parquet('customers.parquet')\n")
