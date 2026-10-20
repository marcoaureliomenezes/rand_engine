# DataGenerator — pandas DataFrames from a RandSpec

`DataGenerator` turns a RandSpec (a dict, or a callable returning one) into a pandas DataFrame,
an infinite stream of dicts, files, or one SQLite output table. Every Python block in this guide runs in CI, in order.

```python
from rand_engine import DataGenerator

spec = {
    "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}},
}

df = DataGenerator(spec, seed=42).size(1_000).get_df()
assert list(df.columns) == ["user_id", "age"]
assert df["age"].between(18, 80).all()
```

## API

<!-- derived-from: data-generator sha256:511ff7f3a370 -->

| Call | Does |
|---|---|
| `DataGenerator(spec, seed=None)` | validates the spec at once (`SpecValidationError`); owns one `np.random.default_rng(seed)` |
| `.size(n)` | rows per `get_df`, total rows in one batch `write`, or rows per stream microbatch; `n` may be a callable returning an int |
| `.transformers([f, ...])` | functions `DataFrame -> DataFrame`, applied in order after generation |
| `.get_df()` | one DataFrame of `size` rows |
| `.stream_dict(min_throughput=1, max_throughput=10)` | an infinite generator of dicts, sleeping `1/uniform(min, max)` s after each |
| `.write` / `.writeStream` | file writers, see [3_WRITING_FILES.md](3_WRITING_FILES.md) |

Calling `get_df` without `.size` raises `RandEngineError`.

## Seeds

<!-- derived-from: data-generator sha256:511ff7f3a370 -->

A seed fixes the output: the same spec, seed and size give the same frame. Each generator owns
its own `numpy.random.Generator` (PCG64), so generators never share or reset NumPy's global state.
Calls on one generator continue its sequence; they do not repeat it.

```python
a = DataGenerator(spec, seed=7).size(100).get_df()
b = DataGenerator(spec, seed=7).size(100).get_df()
assert a.equals(b)

gen = DataGenerator(spec, seed=7).size(100)
assert not gen.get_df().equals(gen.get_df())
```

## Methods

<!-- derived-from: generation-methods sha256:1552dc309621 -->

Each column is `{"method": <name>, "kwargs": {...}}`. Bounds of `integers` are inclusive. A method that generates text gives a `string[pyarrow]` column (`pd.ArrowDtype(pa.string())`) whose nulls are `pd.NA`; numeric, boolean and datetime columns are unchanged. An embedded transformer's output dtype is whatever the transformer returns.

| Method | Required kwargs | Optional kwargs | Column fields |
|---|---|---|---|
| `integers` | `min`, `max` | `int_type` (default `int32`) | — |
| `int_zfilled` | `length` (integer 1…18) | — | — |
| `floats` | `min`, `max` | `decimals` (default 2) | — |
| `floats_normal` | `mean`, `std` | `decimals` (default 2) | — |
| `booleans` | — | `true_prob` (default 0.5) | — |
| `distincts` | `distincts` (list) | — | — |
| `distincts_prop` | `distincts` (dict value → integer weight) | — | — |
| `unix_timestamps` | `start`, `end` | `date_format` (default `%Y-%m-%d`) | — |
| `dates` | `start`, `end` | `date_format` (default `%Y-%m-%d`) | — |
| `uuid4` | — | — | — |
| `exponential` | — | `scale` (default 1.0), `decimals` (default 2) | — |
| `lognormal` | — | `mean` (default 0.0), `std` (default 1.0), `decimals` (default 2) | — |
| `poisson` | — | `lam` (default 1.0) | — |
| `zipf` | — | `a` (default 2.0) | — |
| `constant` | `value` (a scalar) | — | — |
| `distincts_map` | `distincts` (dict key → list of values) | — | `cols` (exactly 2 names) |
| `distincts_map_prop` | `distincts` (dict key → `[[value, weight], ...]`) | — | `cols` (exactly 2 names) |
| `distincts_multi_map` | `distincts` (dict key → one list per level) | — | `cols` (levels + 1 names) |
| `complex_distincts` | `pattern`, `replacement`, `templates` | — | — |
| `pk` | — | `style`, `start`, `step`, `domain`, `key`, `format`; see [4_CONSTRAINTS.md](4_CONSTRAINTS.md) | — |
| `fk` | `parent`, `parent_size` | `skew`, `born_before`; see [4_CONSTRAINTS.md](4_CONSTRAINTS.md) | — |

**Column fields** are required keys beside `kwargs`, not optional kwargs. Only the three map
methods require `cols`; the global optional modifiers are documented separately below.

`dates` and `unix_timestamps` parse `start` and `end` with `date_format`. A `dates` value is a
string drawn at whole-second resolution in UTC; its `date_format` may use only the directives
`%Y %m %d %H %M %S %f` (`%f` renders `000000`). Any other directive fails validation on both
engines, naming the supported set.

```python
from rand_engine.validators.exceptions import SpecValidationError

for length in (1, 18):
    DataGenerator({"id": {"method": "int_zfilled", "kwargs": {"length": length}}})

for length in (0, 19):
    try:
        DataGenerator({"id": {"method": "int_zfilled", "kwargs": {"length": length}}})
    except SpecValidationError:
        pass
    else:
        raise AssertionError("expected int_zfilled length refusal")

spec = {
    "price": {"method": "floats", "kwargs": {"min": 1, "max": 100, "decimals": 2}},
    "status": {"method": "distincts_prop", "kwargs": {"distincts": {"paid": 9, "refunded": 1}}},
    "created_at": {"method": "dates", "kwargs": {
        "start": "2024-01-01 00:00:00", "end": "2024-12-31 23:59:59",
        "date_format": "%Y-%m-%d %H:%M:%S"}},
    "epoch": {"method": "unix_timestamps", "kwargs": {"start": "2024-01-01", "end": "2024-12-31"}},
}
df = DataGenerator(spec, seed=1).size(1_000).get_df()
assert df["created_at"].str.match(r"^2024-\d\d-\d\d \d\d:\d\d:\d\d$").all()  # .str.* predicates return bool[pyarrow]
```

```python
text_df = DataGenerator({"status": {"method": "distincts", "kwargs": {"distincts": ["paid", "refunded"]}}}, seed=1).size(10).get_df()
assert str(text_df["status"].dtype) == "string[pyarrow]"
```

`exponential`, `lognormal`, `poisson`, `zipf` and `constant` run on the NumPy engine only.

```python
from rand_engine.validators.exceptions import SpecValidationError

spec = {
    "wait_s": {"method": "exponential", "kwargs": {"scale": 2.5}},
    "amount": {"method": "lognormal", "kwargs": {"mean": 3.0, "std": 0.5}},
    "visits": {"method": "poisson", "kwargs": {"lam": 4}},
    "rank": {"method": "zipf", "kwargs": {"a": 1.5}},
    "source": {"method": "constant", "kwargs": {"value": "web"}},
}
df = DataGenerator(spec, seed=1).size(1_000).get_df()
assert (df["wait_s"] > 0).all() and (df["rank"] >= 1).all()
assert (df["source"] == "web").all()
```

### Float rules

- `decimals` is an integer with |decimals| ≤ 308 for every float method; beyond that the spec fails validation. `exponential` and `lognormal` take only `decimals ≥ 0`.
- `floats` draws on the `decimals` grid between `min` and `max`. A grid of more than 2^53 steps, or a grid end (bound times 10^`decimals`) beyond int64, draws uniformly within [`min`, `max`] instead.
- Bounds are compared in float64: an integer bound above 2^53 that a double cannot hold may round to the nearest double.
- Rounding never turns a finite draw into `inf`. Parameters near the float64 limit can still draw `inf` from the distribution itself; that is accepted.
- `poisson` `lam` is capped at 10^6.

```python
for bad in ({"method": "floats", "kwargs": {"min": 0, "max": 1, "decimals": 309}},
            {"method": "poisson", "kwargs": {"lam": 2_000_000}}):
    try:
        DataGenerator({"x": bad})
    except SpecValidationError:
        pass
    else:
        raise AssertionError("expected SpecValidationError")
```

### Null and anomaly rates

Any single-column NumPy-engine method may carry `null_rate` (share of rows set to null) and `anomaly_rate` (share
replaced by a draw from `anomaly_values`, a non-empty list of scalars required when the rate is
above 0). Both are in [0, 1]; anomalies apply first, then nulls. `pk`, `fk` and the multi-column methods
(`distincts_map`, `distincts_map_prop`, `distincts_multi_map`, `complex_distincts`) refuse them, and so does SparkGenerator.

```python
spec = {
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}, "null_rate": 0.1},
    "price": {"method": "floats", "kwargs": {"min": 1, "max": 100},
              "anomaly_rate": 0.05, "anomaly_values": [-1.0, 9999.0]},
}
df = DataGenerator(spec, seed=5).size(2_000).get_df()
assert df["age"].isna().any() and df["price"].isin([-1.0, 9999.0]).any()

for bad in ({"id": {"method": "pk", "kwargs": {"start": 1}, "null_rate": 0.1}},
            {"d": {"method": "distincts_map", "cols": ["device", "os"], "null_rate": 0.1,
                   "kwargs": {"distincts": {"phone": ["android", "ios"]}}}},
            {"x": {"method": "exponential", "kwargs": {"scale": 2, "decimals": -1}}}):
    try:
        DataGenerator(bad)
    except SpecValidationError:
        pass
    else:
        raise AssertionError("expected SpecValidationError")
```

### Multi-column methods (NumPy engine only)

These take a `cols` list naming the columns they produce.

| Method | `distincts` shape | Columns |
|---|---|---|
| `distincts_map` | `{key: [value, ...]}` | `cols[0]` = the key, `cols[1]` = a value |
| `distincts_map_prop` | `{key: [(value, weight), ...]}` | `cols[0]` = the key, `cols[1]` = a value |
| `distincts_multi_map` | `{key: [[a, ...], [b, ...]]}` | the key, then one column per inner list (cartesian product); `cols` must name levels + 1 columns, any other count fails validation |

`complex_distincts` fills each `replacement` character of `pattern` with one template column.

```python
spec = {
    "device_os": {"method": "distincts_map", "cols": ["device", "os"],
                  "kwargs": {"distincts": {"phone": ["android", "ios"], "desktop": ["linux", "windows"]}}},
    "company": {"method": "distincts_multi_map", "cols": ["sector", "sub_sector", "size"],
                "kwargs": {"distincts": {"tech": [["software", "hardware"], ["small", "large"]]}}},
    "ip": {"method": "complex_distincts", "kwargs": {
        "pattern": "x.x.x.x", "replacement": "x",
        "templates": [
            {"method": "distincts", "kwargs": {"distincts": ["10", "192"]}},
            {"method": "integers", "kwargs": {"min": 0, "max": 255}},
            {"method": "integers", "kwargs": {"min": 0, "max": 255}},
            {"method": "integers", "kwargs": {"min": 1, "max": 254}},
        ]}},
}
df = DataGenerator(spec, seed=1).size(500).get_df()
assert list(df.columns) == ["device", "os", "sector", "sub_sector", "size", "ip"]
assert set(zip(df["device"], df["os"])) <= {("phone", "android"), ("phone", "ios"), ("desktop", "linux"), ("desktop", "windows")}
```

## Migration to `kwargs`

`kwargs` is the only parameter key. A column carrying `args`, `splitable`, `sep` or `pk` as a key
raises `SpecValidationError` (`pk` stays a method, see [4_CONSTRAINTS.md](4_CONSTRAINTS.md)).

```python
for key in ("args", "splitable", "sep", "pk"):
    try:
        DataGenerator({"age": {"method": "integers", "kwargs": {"min": 0, "max": 9}, key: 1}})
    except SpecValidationError:
        pass
    else:
        raise AssertionError(key)
```

## Transformers

<!-- derived-from: data-generator sha256:511ff7f3a370 -->

A column may carry `"transformers"`: functions applied value by value. `.transformers([...])` takes
whole-frame functions, run after the column ones.

```python
spec = {
    "name": {"method": "distincts", "kwargs": {"distincts": ["ana", "bia"]},
             "transformers": [str.upper]},
    "age": {"method": "integers", "kwargs": {"min": 10, "max": 30}},
}

def age_group(df):
    df["adult"] = df["age"] >= 18
    return df

df = DataGenerator(spec, seed=3).size(100).transformers([age_group]).get_df()
assert set(df["name"]) <= {"ANA", "BIA"}
assert (df["adult"] == (df["age"] >= 18)).all()
assert df["name"].dtype == object  # a transformer's output dtype is what it returns
```

## Validation

<!-- derived-from: rand-spec-grammar sha256:ecbce4973b7e -->

An invalid spec raises `SpecValidationError` (a `RandEngineError`) on construction, listing every
error with a corrected example.

```python
try:
    DataGenerator({"age": {"method": "integers", "kwargs": {"min": 0}}})
except SpecValidationError as error:
    assert "max" in str(error)
else:
    raise AssertionError("expected SpecValidationError")
```

## Streaming dicts

<!-- derived-from: data-generator sha256:511ff7f3a370 -->

`stream_dict` never ends: it generates `size` rows per microbatch, converts datetime columns to
strings and adds `timestamp_created` (epoch seconds) to each record. Stop it yourself.

After that unchanged normalization, every microbatch uses pandas records, preserving public
Python values for scalar, nested, mixed, custom and extension values, and non-string labels.

```python
from itertools import islice

spec = {"user_id": {"method": "int_zfilled", "kwargs": {"length": 8}}}
stream = DataGenerator(spec, seed=1).size(10).stream_dict(min_throughput=500, max_throughput=1000)
records = list(islice(stream, 25))
assert len(records) == 25 and set(records[0]) == {"user_id", "timestamp_created"}

scalar_records = list(islice(
    DataGenerator({"value": {"method": "integers", "kwargs": {"min": 1, "max": 3}}}, seed=3)
    .size(2).stream_dict(500, 1000), 2
))
nested_records = list(islice(
    DataGenerator({"value": {"method": "distincts", "kwargs": {"distincts": [{"nested": [1, 2]}]}}}, seed=3)
    .size(1).stream_dict(500, 1000), 1
))
assert isinstance(nested_records[0]["value"], dict)
```
