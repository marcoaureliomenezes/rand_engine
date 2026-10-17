---
name: rand-engine
description: Generates synthetic data fast from a declarative RandSpec (a dict of column -> method + kwargs) with the rand-engine Python library. Use it for fake or test data, mock pandas DataFrames, stress-test data, Kafka-style event streams, related tables with pk/fk, Spark DataFrames or Faker pools, and whenever rand-engine or RandSpec is mentioned.
---

# rand-engine

Python + NumPy library: one spec dict yields a seeded pandas DataFrame, an infinite dict stream, csv/json/parquet files or a Spark DataFrame. Full docs: https://marcoaureliomenezes.github.io/rand_engine/ (machine-readable index: `llms.txt`; per-class API: the Reference page).

## Install

```bash
pip install rand-engine
pip install "rand-engine[faker]"   # only for Faker pools
```

PySpark is not a dependency: bring your own session.

## The RandSpec grammar

A spec maps each column name to `{"method": ..., "kwargs": {...}}`. Build with `DataGenerator(spec, seed=None)`, set rows with `.size(n)`, then `.get_df()` (pandas), `.stream_dict(min_throughput, max_throughput)` (endless dicts) or `.write` / `.writeStream`.

Optional column keys:

| Key | Effect |
|---|---|
| `null_rate` | share of rows set to null (0 to 1) |
| `anomaly_rate` + `anomaly_values` | share of rows replaced by a draw from the non-empty list `anomaly_values` |
| `transformers` | list of functions applied value by value |
| `cols` | names of the columns a correlated method produces (`distincts_map`, `distincts_map_prop`, `distincts_multi_map`) |

`null_rate` and `anomaly_rate` work on single-column NumPy-engine methods only: `pk`, `fk`, `distincts_map`, `distincts_map_prop`, `distincts_multi_map` and `complex_distincts` refuse them. `.transformers([f, ...])` takes whole-frame functions (DataFrame -> DataFrame), run after the column ones. The same spec, seed and size always give the same frame.

```python
from rand_engine import DataGenerator

spec = {
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}, "null_rate": 0.1},
    "plan": {"method": "distincts_prop", "kwargs": {"distincts": {"free": 8, "pro": 2}},
             "transformers": [str.upper]},
    "spend": {"method": "floats", "kwargs": {"min": 0, "max": 500, "decimals": 2},
              "anomaly_rate": 0.05, "anomaly_values": [-1.0, 99999.0]},
    "device_os": {"method": "distincts_map", "cols": ["device", "os"],
                  "kwargs": {"distincts": {"phone": ["android", "ios"], "pc": ["linux", "windows"]}}},
}

def flag_adult(df):
    df["adult"] = df["age"] >= 21
    return df

df = DataGenerator(spec, seed=42).size(1_000).transformers([flag_adult]).get_df()
assert df.shape == (1_000, 7) and set(df["plan"]) <= {"FREE", "PRO"}
assert DataGenerator(spec, seed=42).size(1_000).transformers([flag_adult]).get_df().equals(df)
```

## Choosing a method

Every method below runs on `DataGenerator` (NumPy). The last column says whether `SparkGenerator` accepts it.

| Method | Required kwargs | Optional kwargs | Column fields | Produces | Spark |
|---|---|---|---|---|---|
| `integers` | `min`, `max` | `int_type` | — | ints in range | yes |
| `int_zfilled` | `length` | — | — | zero-padded digit string | yes |
| `floats` | `min`, `max` | `decimals` | — | uniform floats | yes |
| `floats_normal` | `mean`, `std` | `decimals` | — | normal floats | yes |
| `booleans` | — | `true_prob` | — | bools | yes |
| `distincts` | `distincts` | — | — | uniform pick from a list | yes |
| `distincts_prop` | `distincts` | — | — | weighted pick from a dict | yes |
| `unix_timestamps` | `start`, `end` | `date_format` | — | epoch seconds | yes |
| `dates` | `start`, `end` | `date_format` | — | date strings | yes |
| `uuid4` | — | — | — | uuid strings | yes |
| `exponential` | — | `scale`, `decimals` | — | skewed positive floats | refused |
| `lognormal` | — | `mean`, `std`, `decimals` | — | heavy-tailed floats | refused |
| `poisson` | — | `lam` | — | counts | refused |
| `zipf` | — | `a` | — | rank-skewed ints | refused |
| `constant` | `value` | — | — | the same scalar in every row | refused |
| `distincts_map` | `distincts` | — | `cols` | correlated key/value columns | NULL + warning |
| `distincts_map_prop` | `distincts` | — | `cols` | weighted correlated pair | NULL + warning |
| `distincts_multi_map` | `distincts` | — | `cols` | correlated columns, one per level | NULL + warning |
| `complex_distincts` | `pattern`, `replacement`, `templates` | — | — | strings built from templates | NULL + warning |
| `pk` | — | `style`, `start`, `step`, `domain`, `key`, `format` | — | unique keys | yes |
| `fk` | `parent`, `parent_size` | `skew`, `born_before` | — | references to parent keys | yes |

**Column fields** are required keys outside `kwargs`. Only the three map methods require `cols`;
`null_rate`, `anomaly_rate`, and `anomaly_values` are global NumPy-only modifiers.

`dates` `date_format` accepts `%Y %m %d %H %M %S %f` only. Spark refuses `uint64` and integer domains wider than 2**53; it also refuses `int_zfilled` length 16 or above. The four correlated methods validate with a warning and give a NULL column. `null_rate` and `anomaly_rate` are NumPy only. `RandSpecs.faker_pool("name", locale="pt_BR", pool_size=500, seed=0)` returns a `distincts` spec and needs `rand-engine[faker]`; `RandSpecs.from_schema(arrow_schema, overrides={...})` builds a validated RandSpec from supported Arrow families. For the complete boundaries, factory inventory and runnable examples, see the [method guide](https://marcoaureliomenezes.github.io/rand_engine/1_DATA_GENERATOR/) and [recipes](https://marcoaureliomenezes.github.io/rand_engine/5_RECIPES/).

## Related tables: pk and fk

`pk` is unique by construction: `style` `"sequence"` (default; `start`, `step`) or `"permuted"` (needs `domain`, optional `key`), with an optional `format` such as `"C-{:06d}"`. `fk` takes `parent` (the parent's exact `pk` column spec) and `parent_size` (rows the parent generated), plus optional `skew` (> 0 gives Zipf hot parents). Nothing is stored: the child rebuilds parent keys from the parent spec.

```python
customer_id = {"method": "pk", "kwargs": {"start": 1, "format": "C-{:04d}"}}

customers = DataGenerator({
    "customer_id": customer_id,
    "city": {"method": "distincts", "kwargs": {"distincts": ["Rio", "Recife"]}},
}, seed=1).size(500).get_df()

orders = DataGenerator({
    "order_id": {"method": "pk", "kwargs": {"start": 1}},
    "customer_id": {"method": "fk", "kwargs": {"parent": customer_id, "parent_size": 500, "skew": 1.1}},
}, seed=2).size(2_000).get_df()

assert customers["customer_id"].is_unique
assert orders["customer_id"].isin(customers["customer_id"]).all()
```

`SparkGenerator` accepts the same stateless key definitions. Its `seed` applies only to `pk` and
`fk`; ordinary Spark methods remain unseeded. It computes key columns with a key-only
`mapInPandas` adapter over source row indexes and keeps ordinary columns native to Spark.

## Sinks

`gen.write` is a batch writer: `.format("csv" | "parquet" | "json")`, `.mode("overwrite" | "append")`, `.option(k, v)` / `.options(k=v, ...)`, then `.save(path)`. Only documented options are accepted; anything else raises `RandEngineError` naming the accepted ones. Common options: `compression`, `sep` (csv), `numFiles` (a folder of `part_<id>` files), `maxRowsPerBatch` (bounded memory). `gen.writeStream` adds `.trigger(frequency=seconds)` and the `timeout` option, writes a microbatch per trigger, and `.start(path)` blocks until the timeout.

```python
gen = DataGenerator({
    "id": {"method": "pk", "kwargs": {"start": 1}},
    "name": {"method": "distincts", "kwargs": {"distincts": ["ana", "bia"]}},
}, seed=1).size(1_000)

gen.write.format("parquet").save("out/clients.parquet")
gen.write.format("csv").options(numFiles=2, sep=";").save("out/clients.csv")

import os
assert os.path.exists("out/clients.parquet") and len(os.listdir("out/clients")) == 2
```

For Kafka or any queue, iterate `.stream_dict(min_throughput=..., max_throughput=...)`: each record is a dict with `timestamp_created` added; send it with your own client. It never ends, so stop it yourself.

```python
from itertools import islice

stream = DataGenerator({"event_id": {"method": "pk", "kwargs": {"start": 1}}}, seed=3).size(10)
records = list(islice(stream.stream_dict(min_throughput=500, max_throughput=1000), 25))
assert [r["event_id"] for r in records] == list(range(1, 26))
```

## Spark

`SparkGenerator(spark, F, spec, seed=None).size(n).get_df()` returns a Spark DataFrame. Ordinary
columns use native expressions; `pk` and `fk` use a key-only `mapInPandas` adapter over source row
indexes, and `seed` affects only those key columns. It has no `.transformers` or `.write`: use
Spark's `df.write`. It refuses the methods marked "refused" above with a `SpecValidationError` that
points at `DataGenerator`.

```python no-run
from pyspark.sql import SparkSession, functions as F
from rand_engine import SparkGenerator

spark = SparkSession.builder.getOrCreate()
spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
df = SparkGenerator(spark, F, spec).size(1_000).get_df()
```

## Getting started

```bash
rand-engine list                  # slugs and what each teaches
rand-engine get-started lake      # writes a runnable example script; --out DIR picks the folder
```

Slugs: `test-data`, `lake`, `kafka`, `databricks`, `faker`. It refuses to overwrite an existing file.

## Errors

`DataGenerator` and `SparkGenerator` validate the spec on construction. `SpecValidationError` (a `RandEngineError`) collects every problem at once (with a corrected example for a missing parameter), and its footer points to the docs site. Read the whole message and fix all items before retrying.

```python
from rand_engine.validators.exceptions import SpecValidationError

try:
    DataGenerator({"age": {"method": "integers", "kwargs": {"min": 0}}})
except SpecValidationError as error:
    assert "max" in str(error)
else:
    raise AssertionError("expected SpecValidationError")
```

## Rules when using this skill

- Generate synthetic data only; never put real or personal data in a spec.
- Keep examples small (at most 10^4 rows) and write to relative paths.
- Quote no speed numbers; point to the Benchmarks page instead.
