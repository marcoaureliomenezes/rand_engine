"""Decoy: a pandas-only make.py, rand-engine never builds the frame."""
import subprocess
import sys
from pathlib import Path

Path("make.py").write_text(
    "import numpy as np\nimport pandas as pd\n\n"
    "rng = np.random.default_rng(1)\n"
    "pd.DataFrame({'id': range(1, 1001), 'name': rng.choice(['ana', 'bia', 'caio'], 1000),\n"
    "              'amount': rng.integers(1, 501, 1000), 'status': rng.choice(['new', 'paid'], 1000)}).to_parquet('out.parquet')\n")
subprocess.run([sys.executable, "make.py"], check=True)
