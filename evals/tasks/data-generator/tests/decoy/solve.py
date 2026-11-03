import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
salary = rng.uniform(30000, 120000, 500).round(2)
age = rng.integers(18, 81, 500).astype(float)
age[rng.random(500) < 0.1] = np.nan
pd.DataFrame({"age": age, "salary": salary, "salary_k": salary / 1000}).to_parquet("users.parquet")
