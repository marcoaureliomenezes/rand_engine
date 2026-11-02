---
description: SparkGenerator guide with the call table, the supported and refused method table, mixed-type pools, int_zfilled and integer width limits, and key columns.
---
# SparkGenerator — Spark DataFrames from a RandSpec

One spec runs on a laptop with `DataGenerator` and on Databricks with `SparkGenerator`. On Spark,
dbldatagen is faster: 0.516 s against 1.341 s at 1M rows (one CI run, three samples, medians; run
39153239357, see [comparison.md](comparison.md)).

`SparkGenerator` builds ordinary columns with native Spark expressions over `spark.range(size)`.
For `pk` and `fk`, it passes source row indexes to the same stateless key authority as
`DataGenerator` through a key-only `mapInPandas` adapter. PySpark is not a dependency of
`rand-engine`: bring your own session. CI runs the
Spark tests on Linux, macOS and Windows with Python 3.11–3.14; the Windows Spark skip applies from Python 3.12.

```python
from pyspark.sql import SparkSession, functions as F
from rand_engine import DataGenerator, SparkGenerator

spark = SparkSession.builder.getOrCreate()

spec = {
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}},
    "is_active": {"method": "booleans", "kwargs": {"true_prob": 0.7}},
    "signup": {"method": "dates", "kwargs": {"start": "2020-01-01", "end": "2023-12-31", "date_format": "%Y-%m-%d"}},
}

df = SparkGenerator(spark, F, spec).size(1_000).get_df()
assert df.count() == 1_000
assert df.columns == ["user_id", "age", "is_active", "signup"]
```

## API

<!-- derived-from: spark-generator sha256:74f84215e13e -->

| Call | Does |
|---|---|
| `SparkGenerator(spark, F, spec)` | validates the spec at once (`SpecValidationError`) |
| `.size(n)` | rows to generate |
| `.get_df()` | a Spark DataFrame; the `spark.range` `id` column is dropped unless the spec names `id` |

`seed` applies to `pk` and `fk` only; ordinary Spark methods remain unseeded. There is no
`.transformers` or `.write`: use Spark's own `withColumn` and `df.write`.

## Methods

<!-- derived-from: spark-generator sha256:74f84215e13e -->
<!-- derived-from: generation-methods sha256:79e2694810ad -->

The table records validation's current outcome for every RandSpec method. `yes` means Spark produces
the column; `refused` means use `DataGenerator`.

| Method | Spark |
|---|---|
| `integers` | yes |
| `int_zfilled` | yes |
| `floats` | yes |
| `floats_normal` | yes |
| `booleans` | yes |
| `distincts` | yes |
| `distincts_prop` | yes |
| `unix_timestamps` | yes |
| `dates` | yes |
| `uuid4` | yes |
| `exponential` | refused |
| `lognormal` | refused |
| `poisson` | refused |
| `zipf` | refused |
| `constant` | refused |
| `distincts_map` | refused |
| `distincts_map_prop` | refused |
| `distincts_multi_map` | refused |
| `complex_distincts` | refused |
| `pk` | yes |
| `fk` | yes |

The accepted ordinary methods use the same kwargs as [1_DATA_GENERATOR.md](1_DATA_GENERATOR.md).
`pk` and `fk` use the same stateless definitions as `DataGenerator`; a Spark `seed` affects those
key columns only. A `dates` `date_format` is limited to `%Y %m %d %H %M %S %f`, as on the NumPy
engine. The five NumPy-only distributions/constants, and `null_rate` / `anomaly_rate`, are refused.
`DataGenerator` refuses a mixed `distincts` pool; Spark accepts these: `["x", None]` gives text
and null; `[1, 2.5]` gives doubles; `[1, "x"]` and `[True, "x"]` give text (`"1"`, `"true"`);
`["x", 1, 2.5]` gives text. Ints with `None` give a double column: null with Arrow on, NaN with
Arrow off. Construction refuses, naming the column: container values, a pool
with no inferable value, kinds Spark cannot merge in order (`[1, True]`, `[1, 2.5, "x"]`), date,
timestamp or binary beside text, and integers outside int64 in a numeric pool.
`kwargs` is the only parameter key; `args`, `splitable`, `sep` and `pk` as column keys are also
refused.
Spark accepts `int_zfilled` only through length 15, refuses `uint64`, and refuses integer domains
whose inclusive width exceeds 2**53 because it uses an exact double carrier for those bounds.

```python
from rand_engine.validators.exceptions import SpecValidationError

correlated_specs = {
    "pair": {"method": "distincts_map", "cols": ["kind", "value"],
             "kwargs": {"distincts": {"a": ["b"]}}},
    "weighted_pair": {"method": "distincts_map_prop", "cols": ["kind", "value"],
                      "kwargs": {"distincts": {"a": [["b", 1]]}}},
    "levels": {"method": "distincts_multi_map", "cols": ["kind", "value"],
               "kwargs": {"distincts": {"a": [["b"]]}}},
    "templated": {"method": "complex_distincts",
                  "kwargs": {"pattern": "<x>", "replacement": "x", "templates": []}},
}
for column, definition in correlated_specs.items():
    try:
        SparkGenerator(spark, F, {column: definition})
    except SpecValidationError as error:
        assert "DataGenerator" in str(error)
    else:
        raise AssertionError("expected SpecValidationError")
```

```python
parent = {"method": "pk", "kwargs": {"start": 100}}
key_spec = {
    "customer_id": parent,
    "buyer_id": {"method": "fk", "kwargs": {"parent": parent, "parent_size": 8}},
}
keyed = SparkGenerator(spark, F, key_spec, seed=7).size(8).get_df()
assert keyed.columns == ["customer_id", "buyer_id"]
spark_keys = [tuple(row) for row in keyed.orderBy("customer_id").collect()]
pandas_keys = list(DataGenerator(key_spec, seed=7).size(8).get_df().itertuples(index=False, name=None))
assert spark_keys == pandas_keys

from rand_engine.validators.exceptions import SpecValidationError

for length in (15,):
    SparkGenerator(spark, F, {"id": {"method": "int_zfilled", "kwargs": {"length": length}}})

for spec in (
    {"id": {"method": "int_zfilled", "kwargs": {"length": 16}}},
    {"id": {"method": "integers", "kwargs": {"min": 0, "max": 10, "int_type": "uint64"}}},
    {"id": {"method": "integers", "kwargs": {"min": 0, "max": 2**53, "int_type": "int64"}}},
):
    try:
        SparkGenerator(spark, F, spec)
    except SpecValidationError:
        pass
    else:
        raise AssertionError("expected Spark carrier or width refusal")

try:
    SparkGenerator(spark, F, {"visits": {"method": "poisson", "kwargs": {"lam": 4}}})
except SpecValidationError as error:
    assert "DataGenerator" in str(error)
else:
    raise AssertionError("expected SpecValidationError")
```

## Writing

<!-- derived-from: spark-generator sha256:74f84215e13e -->

Use Spark's own `df.write`; rand-engine does not own Spark writing.
