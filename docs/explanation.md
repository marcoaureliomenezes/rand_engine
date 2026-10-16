# Explanation

## The RandSpec model

A RandSpec is a plain dict: each column names a `method` and its `kwargs`. The library validates it, never mutates it, and a spec that validates generates.

## NumPy core, Spark supported

`DataGenerator` is Python, NumPy and pandas alone. `SparkGenerator` runs the same idea natively on Spark, but Spark is never the center and never required. For measured speed see [Benchmarks](BENCHMARKS.md).

## Sink-agnostic output

The generator produces frames and record streams; where they go is yours: Kafka and other queues, a data lake or object storage, files, a database, Spark.

## Faker on top, through pools

Faker is slow per value. Draw a small pool once, then let rand-engine sample it at [NumPy speed](BENCHMARKS.md). Faker complements the core and is never required.

```python
from rand_engine import DataGenerator

names = ["Ana", "Bruno", "Carla"]
df = DataGenerator({"name": {"method": "distincts", "kwargs": {"distincts": names}}}, seed=1).size(100).get_df()
assert df["name"].isin(names).all()
```

## Seeds and reproducibility

Each generator owns its NumPy `Generator`, so the same spec, seed and size give the same frame and the global NumPy state is never touched.

## Keys without state

`pk` and `fk` are stateless key columns computed from the seed and the row index. A child `fk` rebuilds its parent's `pk` value, so related tables stay consistent across batches, streams and processes with no checkpoint store.
