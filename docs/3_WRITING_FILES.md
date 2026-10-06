# Writing files — `write` and `writeStream`

`DataGenerator.write` writes a batch once; `DataGenerator.writeStream` writes a microbatch per
trigger until a timeout. Both take `.format()`, `.mode()`, `.option()` / `.options()`.

```python
import os
from rand_engine import DataGenerator

spec = {
    "id": {"method": "pk", "kwargs": {"start": 1}},
    "name": {"method": "distincts", "kwargs": {"distincts": ["ana", "bia"]}},
    "active": {"method": "booleans", "kwargs": {}},
}
gen = DataGenerator(spec, seed=1).size(1_000)

gen.write.format("parquet").save("out/clients.parquet")
gen.write.format("csv").option("compression", "gzip").save("out/clients.csv")
gen.write.format("json").options(numFiles=4).mode("overwrite").save("out/clients_json")

assert os.path.exists("out/clients.parquet") and os.path.exists("out/clients.csv.gz")
assert len(os.listdir("out/clients_json")) == 4
```

## Writer contract

- `csv` and `parquet` are written by pyarrow; `json` by pandas (`orient="records"`, one record per line).
- Only the options below are accepted. Any other raises `RandEngineError` naming it and listing the
  accepted ones, before any file is deleted or written.

| Format | Options |
|---|---|
| `csv` | `sep` (delimiter, default `,`); `compression`: `gzip`, `bz2`, `xz`, `zip`; `index`: only `False` (Arrow writes no index) |
| `parquet` | `compression`: `snappy` (default), `gzip`, `zstd`, `brotli`, `lz4` |
| `json` | `force_ascii`, `indent`, `compression` (`gzip`, `bz2`, `zip`); `orient`: only `"records"` |
| `write` (batch) | `numFiles` (default 1) |
| `writeStream` | `timeout` in seconds (default 20) |

- A column holding mixed types (e.g. ints and strings in one object column) raises
  `RandEngineError` naming the column for `csv` and `parquet`.
- Parquet reads back equal to the frame, values and dtypes, tz-aware columns included.

```python
from rand_engine.validators.exceptions import RandEngineError

try:
    gen.write.format("parquet").option("engine", "fastparquet").save("out/bad.parquet")
except RandEngineError as error:
    assert "engine" in str(error) and "numFiles" in str(error)
else:
    raise AssertionError("expected RandEngineError")
```

## Batch: `write`

- `save(path)` with `numFiles` 1 writes one file at `path`, the format and compression extension
  added when missing (`out/clients.csv` + `gzip` → `out/clients.csv.gz`; parquet never gets one).
- With `numFiles` > 1, `path` (extensions stripped) is a folder of `part_<id>.<ext>` files sharing
  the `size` rows; `mode("overwrite")` (the default) empties that folder first, any other mode
  adds files beside the old ones.
- Keys continue across the files: `pk` values never repeat between parts.

```python
import pandas as pd

gen.write.format("csv").options(numFiles=3, sep=";").save("out/parts.csv")
parts = [pd.read_csv(f"out/parts/{f}", sep=";") for f in sorted(os.listdir("out/parts"))]
ids = pd.concat(parts)["id"]
assert len(ids) == 1_000 and ids.is_unique
```

## Stream: `writeStream`

`start(path)` writes one microbatch of `size` rows to `path/part-<uuid>.<ext>`, sleeps
`trigger(frequency)` seconds and repeats until `timeout` seconds have passed. `mode("overwrite")`
(the default) empties the folder first. `start` blocks until the timeout.

```python
gen.writeStream.format("json").trigger(frequency=0.1).option("timeout", 0.3).start("out/stream.json")
files = os.listdir("out/stream")
assert len(files) >= 2
```

## CSV written by pyarrow

CSV output differs from `pandas.DataFrame.to_csv`:

- booleans are written `true` / `false`;
- integral floats are written `1`, so they read back as int;
- the header and every string value are quoted;
- a naive timestamp's fraction is sized by its column's unit: `ns` (the pandas default)
  `.000000000`, `us` six digits, `ms` three, `s` none;
- an all-midnight naive datetime column is written with its full time
  (`2020-01-01 00:00:00.000000000`), not a bare date;
- a tz-aware column is written in its pandas string form, quoted
  (`2024-01-01 00:00:00+00:00`, `…-03:00`);
- a missing timestamp (NaT) in a multi-column frame is an empty field, never `NaT`;
- in a one-column frame a null is written as a blank line, which `pd.read_csv` skips by default,
  so that row is lost on read-back;
- line endings are always LF, on every OS.

```python
gen.write.format("csv").save("out/check.csv")
with open("out/check.csv", newline="") as file:
    header, first = file.read().split("\n")[:2]
assert header == '"id","name","active"'
assert first.split(",")[2] in ("true", "false")
```
