import numpy as np
import pandas as pd
from rand_engine import DataGenerator

DataGenerator({"product_id": {"method": "pk", "kwargs": {"style": "sequence", "start": 1}}}, seed=42).size(5).get_df()
rng = np.random.default_rng(42)
pd.DataFrame({"product_id": np.arange(1, 5001), "views": rng.zipf(1.5, 5000)}).to_csv("product_views.csv", index=False)
