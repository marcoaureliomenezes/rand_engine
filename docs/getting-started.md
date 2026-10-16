# Getting started

## Install

```bash
pip install rand-engine
pip install "rand-engine[faker]"  # only for Faker pools
```

## Thirty seconds

A spec maps each column to a `method` and its `kwargs`; the seed makes the frame reproducible.

```python
from rand_engine import DataGenerator

spec = {
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}},
    "plan": {"method": "distincts_prop", "kwargs": {"distincts": {"free": 8, "pro": 2}}},
}

df = DataGenerator(spec, seed=42).size(1_000).get_df()
df.to_parquet("users.parquet")
assert df.shape == (1_000, 3) and df["age"].between(18, 80).all()
```

## Scaffold an example

```bash
rand-engine list
rand-engine get-started lake
```

`list` prints the slugs; `get-started <slug>` writes a runnable script into the current directory. Each slug has a tutorial:

- [Test data](tutorials/test-data.md)
- [Lake](tutorials/lake.md)
- [Kafka](tutorials/kafka.md)
- [Databricks](tutorials/databricks.md)
- [Faker](tutorials/faker.md)
