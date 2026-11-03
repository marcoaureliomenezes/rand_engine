import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
pd.DataFrame({
    "id": rng.integers(1, 100001, 100),
    "score": rng.uniform(0, 1, 100).round(3),
}).to_parquet("people.parquet")
