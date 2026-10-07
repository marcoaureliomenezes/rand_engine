# rand-engine

Synthetic data, very fast, from a declarative spec — for batch and streaming, on any platform.

- **Sink-agnostic:** feed Kafka and other queues, data lakes and object storage, files, databases or Spark.
- **NumPy-fast:** the core is Python + NumPy (`DataGenerator`); Spark is supported (`SparkGenerator`), never required.
- **Faker composes on top:** build a small realistic pool with Faker, sample millions of rows from it at NumPy speed.
- **Related tables:** `pk` and `fk` columns keep keys consistent across tables, batches, streams and files.

## Install

<!-- derived-from: public-api sha256:0d1a9b54e4a7 -->

```bash
pip install rand-engine
```

## Quickstart

<!-- derived-from: data-generator sha256:2a69edeee8a2 -->
<!-- derived-from: rand-spec-grammar sha256:7b0eef6f065a -->

A spec maps each column to a `method` and its `kwargs`.

```python
from rand_engine import DataGenerator

spec = {
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}},
    "plan": {"method": "distincts_prop", "kwargs": {"distincts": {"free": 8, "pro": 2}}},
    "signup": {"method": "dates", "kwargs": {"start": "2024-01-01", "end": "2024-12-31"}},
}

df = DataGenerator(spec, seed=42).size(1_000).get_df()
assert df.shape == (1_000, 4) and df["age"].between(18, 80).all()
```

## Seeded reproducibility

<!-- derived-from: data-generator sha256:2a69edeee8a2 -->

The seed is per generator: each `DataGenerator` owns its own NumPy `Generator` (PCG64), so the
caller's NumPy global state is never read or reset. The same spec, seed and size give the same
frame. Values differ from 0.6.x, which drew from the global NumPy seed.

```python
import numpy as np

np.random.seed(0)
state = np.random.get_state()[1].copy()
a = DataGenerator(spec, seed=7).size(100).get_df()
b = DataGenerator(spec, seed=7).size(100).get_df()
assert a.equals(b)
assert (np.random.get_state()[1] == state).all()
```

## Faker pools at scale

<!-- derived-from: generation-methods sha256:b3bed2e747eb -->

Install the optional Faker dependency with `pip install faker` before running this example.
Faker is slow per value; draw a pool once and let rand-engine sample it.

```python
from faker import Faker

fake = Faker()
Faker.seed(0)
names = [fake.name() for _ in range(200)]

people = DataGenerator({"name": {"method": "distincts", "kwargs": {"distincts": names}}}, seed=1).size(10_000).get_df()
assert people["name"].isin(names).all()
```

## Related tables

<!-- derived-from: pk-fk-constraints sha256:f618b12b0b07 -->

Give the child's `fk` the parent's `pk` spec and size: every child key exists in the parent.

```python
customer_pk = {"method": "pk", "kwargs": {"start": 1, "format": "C{:05d}"}}

customers = DataGenerator({"customer_id": customer_pk}, seed=1).size(500).get_df()
orders = DataGenerator({
    "order_id": {"method": "pk", "kwargs": {"start": 1}},
    "customer_id": {"method": "fk", "kwargs": {"parent": customer_pk, "parent_size": 500}},
}, seed=2).size(2_000).get_df()

assert customers["customer_id"].is_unique
assert set(orders["customer_id"]) <= set(customers["customer_id"])
```

## Streams and files

<!-- derived-from: data-generator sha256:2a69edeee8a2 -->
<!-- derived-from: writers-and-streaming sha256:6b17969e7cb2 -->

`stream_dict` yields records forever at a bounded rate; `write` writes csv, json or parquet.

```python
from itertools import islice
import pandas as pd

events = DataGenerator({"event_id": {"method": "pk", "kwargs": {"start": 1}}}, seed=1).size(10)
records = list(islice(events.stream_dict(min_throughput=500, max_throughput=1000), 5))
assert [r["event_id"] for r in records] == [1, 2, 3, 4, 5]

orders_gen = DataGenerator({"order_id": {"method": "pk", "kwargs": {"start": 1}}}, seed=1).size(1_000)
orders_gen.write.format("parquet").save("out/orders.parquet")
assert len(pd.read_parquet("out/orders.parquet")) == 1_000
```

## Learn more

<!-- derived-from: public-api sha256:0d1a9b54e4a7 -->
<!-- derived-from: benchmarks sha256:42b63a34e160 -->

- [DataGenerator](https://github.com/marcoaureliomenezes/rand_engine/blob/master/docs/1_DATA_GENERATOR.md): methods, seeds, streams.
- [SparkGenerator](https://github.com/marcoaureliomenezes/rand_engine/blob/master/docs/2_SPARK_GENERATOR.md): the same spec as a Spark DataFrame.
- [Writing files](https://github.com/marcoaureliomenezes/rand_engine/blob/master/docs/3_WRITING_FILES.md): `write` and `writeStream`, formats and options.
- [Keys](https://github.com/marcoaureliomenezes/rand_engine/blob/master/docs/4_CONSTRAINTS.md): `pk` and `fk` in depth.
- [Recipes](https://github.com/marcoaureliomenezes/rand_engine/blob/master/docs/5_RECIPES.md): Faker pools, queues, parquet lakes, related tables.
- [Benchmarks](https://github.com/marcoaureliomenezes/rand_engine/blob/master/docs/BENCHMARKS.md): rows/µs per method, measured in CI.
- [Changelog](https://github.com/marcoaureliomenezes/rand_engine/blob/master/CHANGELOG.md): the 0.7.0 breaking changes.
- [License](https://github.com/marcoaureliomenezes/rand_engine/blob/master/LICENSE): MIT.
