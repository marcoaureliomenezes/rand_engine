# DataGenerator — pandas DataFrames from a RandSpec

`DataGenerator` turns a RandSpec (a dict, or a callable returning one) into a pandas DataFrame,
an infinite stream of dicts, or files. Every Python block in this guide runs in CI, in order.

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

| Call | Does |
|---|---|
| `DataGenerator(spec, seed=None)` | validates the spec at once (`SpecValidationError`); owns one `np.random.default_rng(seed)` |
| `.size(n)` | rows per `get_df`, per file in `write`, per microbatch in a stream; `n` may be a callable returning an int |
| `.transformers([f, ...])` | functions `DataFrame -> DataFrame`, applied in order after generation |
| `.get_df()` | one DataFrame of `size` rows |
| `.stream_dict(min_throughput=1, max_throughput=10)` | an infinite generator of dicts, sleeping `1/uniform(min, max)` s after each |
| `.write` / `.writeStream` | file writers, see [3_WRITING_FILES.md](3_WRITING_FILES.md) |

Calling `get_df` without `.size` raises `RandEngineError`.

## Seeds

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

Each column is `{"method": <name>, "kwargs": {...}}`. Bounds of `integers` are inclusive.

| Method | Required kwargs | Optional kwargs |
|---|---|---|
| `integers` | `min`, `max` | `int_type` (`int8`…`int64`, `uint8`…`uint64`; default `int32`) |
| `int_zfilled` | `length` | — |
| `floats` | `min`, `max` | `decimals` (default 2) |
| `floats_normal` | `mean`, `std` | `decimals` (default 2) |
| `booleans` | — | `true_prob` (default 0.5) |
| `distincts` | `distincts` (list) | — |
| `distincts_prop` | `distincts` (dict value → integer weight) | — |
| `uuid4` | — | — |
| `unix_timestamps` | `start`, `end` | `date_format` (default `%Y-%m-%d`) |
| `dates` | `start`, `end` | `date_format` (default `%Y-%m-%d`) |
| `pk`, `fk` | see [4_CONSTRAINTS.md](4_CONSTRAINTS.md) | |

`dates` and `unix_timestamps` parse `start` and `end` with `date_format`. A `dates` value is a
string drawn at whole-second resolution in UTC; its `date_format` may use only the directives
`%Y %m %d %H %M %S %f` (`%f` renders `000000`). Any other directive fails validation on both
engines, naming the supported set.

```python
spec = {
    "price": {"method": "floats", "kwargs": {"min": 1, "max": 100, "decimals": 2}},
    "status": {"method": "distincts_prop", "kwargs": {"distincts": {"paid": 9, "refunded": 1}}},
    "created_at": {"method": "dates", "kwargs": {
        "start": "2024-01-01 00:00:00", "end": "2024-12-31 23:59:59",
        "date_format": "%Y-%m-%d %H:%M:%S"}},
    "epoch": {"method": "unix_timestamps", "kwargs": {"start": "2024-01-01", "end": "2024-12-31"}},
}
df = DataGenerator(spec, seed=1).size(1_000).get_df()
assert df["created_at"].str.match(r"^2024-\d\d-\d\d \d\d:\d\d:\d\d$").all()
```

### Multi-column methods (NumPy engine only)

These take a `cols` list naming the columns they produce.

| Method | `distincts` shape | Columns |
|---|---|---|
| `distincts_map` | `{key: [value, ...]}` | `cols[0]` = a value, `cols[1]` = its key |
| `distincts_map_prop` | `{key: [(value, weight), ...]}` | `cols[0]` = the key, `cols[1]` = a value |
| `distincts_multi_map` | `{key: [[a, ...], [b, ...]]}` | the key, then one column per inner list (cartesian product) |

`complex_distincts` fills each `replacement` character of `pattern` with one template column.

```python
spec = {
    "os_device": {"method": "distincts_map", "cols": ["os", "device"],
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
assert list(df.columns) == ["os", "device", "sector", "sub_sector", "size", "ip"]
assert set(zip(df["os"], df["device"])) <= {("android", "phone"), ("ios", "phone"), ("linux", "desktop"), ("windows", "desktop")}
```

## Transformers

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
```

## Validation

An invalid spec raises `SpecValidationError` (a `RandEngineError`) on construction, listing every
error with a corrected example.

```python
from rand_engine.validators.exceptions import SpecValidationError

try:
    DataGenerator({"age": {"method": "integers", "kwargs": {"min": 0}}})
except SpecValidationError as error:
    assert "max" in str(error)
else:
    raise AssertionError("expected SpecValidationError")
```

## Streaming dicts

`stream_dict` never ends: it generates `size` rows per microbatch, converts datetime columns to
strings and adds `timestamp_created` (epoch seconds) to each record. Stop it yourself.

```python
from itertools import islice

spec = {"user_id": {"method": "int_zfilled", "kwargs": {"length": 8}}}
stream = DataGenerator(spec, seed=1).size(10).stream_dict(min_throughput=500, max_throughput=1000)
records = list(islice(stream, 25))
assert len(records) == 25 and set(records[0]) == {"user_id", "timestamp_created"}
```
