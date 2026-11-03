import numpy as np
import pandas as pd
import rand_engine

rng = np.random.default_rng(42)
pd.DataFrame({
    "id": rng.integers(1, 100001, 100),
    "score": rng.uniform(0, 1, 100).round(3),
}).to_parquet("people.parquet")
with open("version.txt", "w", encoding="utf-8") as f:
    f.write(rand_engine.__version__ + "\n")
