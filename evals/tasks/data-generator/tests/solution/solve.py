from rand_engine import DataGenerator

spec = {
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}, "null_rate": 0.1},
    "salary": {"method": "floats", "kwargs": {"min": 30000, "max": 120000, "decimals": 2}},
}
df = (DataGenerator(spec, seed=42)
      .transformers([lambda df: df.assign(salary_k=df["salary"] / 1000)])
      .size(500)
      .get_df())
df.to_parquet("users.parquet")
