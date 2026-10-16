# rand-engine

Synthetic data, very fast, from a declarative `RandSpec` — for batch and streaming, on any platform. The core is Python + NumPy; Spark is supported, never required, and Faker composes on top.

[![PyPI](https://img.shields.io/pypi/v/rand-engine)](https://pypi.org/project/rand-engine/)
[![Python](https://img.shields.io/pypi/pyversions/rand-engine)](https://pypi.org/project/rand-engine/)
[![License](https://img.shields.io/pypi/l/rand-engine)](https://github.com/marcoaureliomenezes/rand_engine/blob/master/LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/marcoaureliomenezes/rand_engine/test_on_push.yml)](https://github.com/marcoaureliomenezes/rand_engine/actions)

## Install

```bash
pip install rand-engine
pip install "rand-engine[faker]"  # optional: Faker pools
```

## 30-second example

A spec maps each column to a `method` and its `kwargs`; the seed makes it reproducible.

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

## When to use it

- Test data for pipelines, with nulls and anomalies on demand.
- Related tables whose `pk` and `fk` keys stay consistent across batches, streams and files.
- Event streams and files for queues, lakes, databases or Spark, at NumPy speed.

## Get-started cases

Each case is a runnable example. `rand-engine list` prints them; `rand-engine get-started <slug>` writes `<slug>.py` (also `python -m rand_engine get-started <slug>`, with `--out DIR` to choose the folder).

- `test-data`: a DataFrame for pipeline tests with `null_rate` and `anomaly_rate`.
- `lake`: `pk`/`fk` related tables written to a Parquet lake.
- `kafka`: an event stream for Kafka, JSON lines to stdout by default.
- `databricks`: a Spark/Databricks notebook on native `SparkGenerator`.
- `faker`: Faker pools sampled at NumPy speed through `RandSpecs.faker_pool`.

## Documentation

Full guides and the method reference live on the [docs site](https://marcoaureliomenezes.github.io/rand_engine/). AI agents: see the [rand-engine skill](https://github.com/marcoaureliomenezes/rand_engine/blob/master/skills/rand-engine/SKILL.md).
