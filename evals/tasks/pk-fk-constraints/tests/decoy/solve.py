import numpy as np
import pandas as pd

rng = np.random.default_rng(1)
pd.DataFrame({"customer_id": np.arange(1, 1001)}).to_parquet("customers.parquet")
pd.DataFrame({"order_id": np.arange(1, 5001), "customer_id": rng.integers(1, 1001, 5000)}).to_parquet("orders.parquet")
