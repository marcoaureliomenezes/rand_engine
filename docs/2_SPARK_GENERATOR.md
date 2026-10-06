# SparkGenerator — Spark DataFrames from a RandSpec

`SparkGenerator` builds the columns with native Spark expressions over `spark.range(size)`; no
pandas step. PySpark is not a dependency of `rand-engine`: bring your own session.

```python
from pyspark.sql import SparkSession, functions as F
from rand_engine import SparkGenerator

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

| Call | Does |
|---|---|
| `SparkGenerator(spark, F, spec)` | validates the spec at once (`SpecValidationError`) |
| `.size(n)` | rows to generate |
| `.get_df()` | a Spark DataFrame; the `spark.range` `id` column is dropped unless the spec names `id` |

There is no seed, no `.transformers`, no `.write`: use Spark's own `withColumn` and `df.write`.

## Methods

Supported, with the same kwargs as [1_DATA_GENERATOR.md](1_DATA_GENERATOR.md): `integers`,
`int_zfilled`, `floats`, `floats_normal`, `booleans`, `distincts`, `distincts_prop`, `uuid4`,
`unix_timestamps`, `dates`. A `dates` `date_format` is limited to `%Y %m %d %H %M %S %f`, as on
the NumPy engine.

- `distincts_map`, `distincts_map_prop`, `distincts_multi_map`, `complex_distincts` validate with a
  warning and produce a NULL string column.
- `pk` and `fk` are refused: they run on the NumPy engine only ([4_CONSTRAINTS.md](4_CONSTRAINTS.md)).
- `args` is refused; use `kwargs`.

```python
from rand_engine.validators.exceptions import SpecValidationError

try:
    SparkGenerator(spark, F, {"id": {"method": "pk", "kwargs": {}}})
except SpecValidationError as error:
    assert "NumPy engine only" in str(error)
else:
    raise AssertionError("expected SpecValidationError")
```

## Writing

Use Spark's own `df.write`; rand-engine does not own Spark writing.
