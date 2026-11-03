"""Reference: fix the wrong method name in spec.py, then write and run make.py."""
import subprocess
import sys
from pathlib import Path

Path("spec.py").write_text(Path("spec.py").read_text().replace('"integer"', '"integers"'))
Path("make.py").write_text(
    "from rand_engine import DataGenerator\n"
    "from spec import spec\n\n"
    'DataGenerator(spec, seed=1).size(1000).get_df().to_parquet("out.parquet")\n')
subprocess.run([sys.executable, "make.py"], check=True)
