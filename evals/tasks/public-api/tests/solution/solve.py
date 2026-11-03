import rand_engine
from rand_engine import DataGenerator

print(rand_engine.__version__)

spec = {
    "id": {"method": "integers", "kwargs": {"min": 1, "max": 100000}},
    "score": {"method": "floats", "kwargs": {"min": 0, "max": 1, "decimals": 3}},
}
df = DataGenerator(spec, seed=42).size(100).get_df()
df.to_parquet("people.parquet")
