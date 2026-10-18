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

`list` prints six starters. Five write runnable scripts into the current directory; run the written file from that directory. `--out DIR` writes to a directory of your choice.

| Use case | Command | File | Run | Prerequisite | Outcome | Guide |
| --- | --- | --- | --- | --- | --- | --- |
| Pipeline test data (`test-data`) | `rand-engine get-started test-data` | `test-data-example.py` | `python test-data-example.py` | `rand-engine` | A 1,000-row DataFrame with null and anomaly counts | [Tutorial](tutorials/test-data.md) |
| Related Parquet tables (`lake`) | `rand-engine get-started lake` | `lake-example.py` | `python lake-example.py` | `rand-engine` | Parquet customer and order tables under `lake/`, read back and joined | [Tutorial](tutorials/lake.md) |
| Kafka or another queue (`kafka`) | `rand-engine get-started kafka` | `kafka-example.py` | `python kafka-example.py` | `rand-engine`; `kafka-python` only to enable the producer | 100 JSON event lines on stdout; the optional producer sends to a configured broker | [Tutorial](tutorials/kafka.md) |
| Spark or Databricks (`databricks`) | `rand-engine get-started databricks` | `databricks-example.py` | `python databricks-example.py` | A Databricks runtime, or PySpark and Java | A native Spark DataFrame is shown with its schema | [Tutorial](tutorials/databricks.md) |
| Faker pools (`faker`) | `rand-engine get-started faker` | `faker-example.py` | `python faker-example.py` | `rand-engine[faker]` | A 10,000-row DataFrame sampled from reproducible name, email and city pools | [Tutorial](tutorials/faker.md) |

## Agent context

The sixth starter is an optional project context for an agent that uses rand-engine. It is not a runnable tutorial:

```bash
rand-engine get-started agent --out PROJECT
```

It writes only `PROJECT/AGENTS.md`. This starter begins in 0.8.0; it is not in the published 0.8.0rc4 wheel. Existing project instructions are preserved: review both files and merge the package-use context into the project's own rules.

Choose [Writing files](3_WRITING_FILES.md) for a direct file writer, [Keys](4_CONSTRAINTS.md) for
related tables, and [Recipes](5_RECIPES.md) for the runnable Kafka-or-queue and Parquet patterns.
For Python, Spark, migration and recovery boundaries, read [Compatibility](compatibility.md).
