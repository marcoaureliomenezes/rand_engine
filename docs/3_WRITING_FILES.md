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

<!-- derived-from: writers-and-streaming sha256:f89f1771153d -->

- `csv` and `parquet` are written by pyarrow; `json` by pandas (`orient="records"`, one record per line).
- Only the options below are accepted. Any other raises `RandEngineError` naming it and listing the
  accepted ones, before any file is deleted or written.

| Format | Options |
|---|---|
| `csv` | `sep` (delimiter, default `,`); `compression`: `gzip`, `bz2`, `xz`, `zip`; `index`: only `False` (Arrow writes no index) |
| `parquet` | `compression`: `snappy` (default), `gzip`, `zstd`, `brotli`, `lz4` |
| `json` | `force_ascii`, `indent`, `compression` (`gzip`, `bz2`, `xz`, `zip`); `orient`: only `"records"` |
| `sqlite` | `table` (required, non-empty table name); `overwrite` or `append`; no file batching or file-format options |
| `write` (batch) | `numFiles` (default 1); `maxRowsPerBatch` (positive int; rows generated and written per batch, so memory stays bounded) |
| `writeStream` | `timeout` in seconds (default 20) |

- A column holding mixed types (e.g. ints and strings in one object column) raises
  `RandEngineError` naming the column for `csv` and `parquet`.
- Parquet reads back equal to the frame in values, tz-aware columns included, and in dtype for every non-text column. A generated text column reads back as `pd.StringDtype("pyarrow")` under the default read and as the frame's `pd.ArrowDtype(pa.string())` with `pd.read_parquet(..., dtype_backend="pyarrow")`.

```python
from rand_engine.validators.exceptions import RandEngineError

try:
    gen.write.format("parquet").option("engine", "fastparquet").save("out/bad.parquet")
except RandEngineError as error:
    assert "engine" in str(error) and "numFiles" in str(error)
else:
    raise AssertionError("expected RandEngineError")
```

Spark: a text column with nulls holds `pd.NA`. To convert such a frame with `spark.createDataFrame`, enable `spark.sql.execution.arrow.pyspark.enabled` first. Without it, `spark.createDataFrame` raises `PySparkTypeError` (`[CANNOT_MERGE_TYPE]`).

## Batch: `write`

<!-- derived-from: writers-and-streaming sha256:f89f1771153d -->

- `save(path)` with `numFiles` 1 writes one file at `path`, the format and compression extension
  added when missing (`out/clients.csv` + `gzip` → `out/clients.csv.gz`; parquet never gets one).
- With `numFiles` > 1, `path` (extensions stripped) is a folder of `part_<id>.<ext>` files sharing
  the `size` rows. The batch writer stages every new file beside the destination and commits only
  after staging succeeds. Only `mode("append")` adds staged parts to an existing folder; every
  other mode replaces the destination folder when the commit succeeds.
- A final file has one schema: with `maxRowsPerBatch` every batch of a file must produce the same
  schema, and `mode("append")` to a single file must match the existing one.
- Keys continue across the files: `pk` values never repeat between parts.

```python
import pandas as pd

gen.write.format("csv").options(numFiles=3, sep=";").save("out/parts.csv")
parts = [pd.read_csv(f"out/parts/{f}", sep=";") for f in sorted(os.listdir("out/parts"))]
ids = pd.concat(parts)["id"]
assert len(ids) == 1_000 and ids.is_unique

spec_log = {"level": {"method": "distincts", "kwargs": {"distincts": ["info", "warn"]}}}
log = DataGenerator(spec_log, seed=2).size(1_000)
log.write.format("csv").options(numFiles=2, maxRowsPerBatch=100).save("out/log.csv")
log.write.format("csv").options(numFiles=2).mode("append").save("out/log.csv")
logs = os.listdir("out/log")
assert len(logs) == 4
assert sum(len(pd.read_csv(f"out/log/{f}")) for f in logs) == 2_000
```

### SQLite table sink

SQLite is a batch-only output sink: use `write.format("sqlite").option("table", name)` and one
of `overwrite` or `append`. Identifiers are quoted and row values are bound. An overwrite stages
the selected table replacement while preserving unrelated tables; append is transactional. SQLite
stores bools and signed 64-bit integers as INTEGER, floats as REAL, strings and ISO dates as TEXT,
bytes as BLOB, and nulls as NULL. Mixed and all-null columns have no declared affinity. It does
not create a primary-key constraint from a RandSpec key, resume files, or accept `numFiles`,
`maxRowsPerBatch`, or other file options.

```python
import sqlite3
from rand_engine.validators.exceptions import RandEngineError

sqlite_path = "out/clients.sqlite"
sqlite_table = 'client "events"'
gen.write.format("sqlite").option("table", sqlite_table).mode("overwrite").save(sqlite_path)
gen.write.format("sqlite").option("table", sqlite_table).mode("append").save(sqlite_path)
with sqlite3.connect(sqlite_path) as database:
    quoted = sqlite_table.replace('"', '""')
    assert database.execute(f'SELECT COUNT(*) FROM "{quoted}"').fetchone()[0] == 2_000

try:
    gen.writeStream.format("sqlite").option("table", "events").start("out/events.sqlite")
except RandEngineError:
    pass
else:
    raise AssertionError("SQLite is batch-only")
```

## Stream: `writeStream`

<!-- derived-from: writers-and-streaming sha256:f89f1771153d -->

`trigger(frequency)` only configures the pause after each write and returns the stream writer.
`start(path)` writes one microbatch of `size` rows to `path/part-<uuid>.<ext>`, sleeps the
configured number of seconds and repeats until `timeout` seconds have passed. `mode("overwrite")`
(the default) clears the folder first. `start` blocks until the timeout.

```python
gen.writeStream.format("json").trigger(frequency=0.1).option("timeout", 0.3).start("out/stream.json")
files = os.listdir("out/stream")
assert len(files) >= 2
```

## CSV written by pyarrow

<!-- derived-from: writers-and-streaming sha256:f89f1771153d -->

CSV output differs from `pandas.DataFrame.to_csv`:

- booleans are written `true` / `false`;
- integral floats are written `1`, so they read back as int;
- the header and every string value are quoted;
- a naive timestamp's fraction follows its column's unit: `ns` `.000000000`, `us` six digits,
  `ms` three, `s` none;
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

## Returned writer reference

`DataGenerator.write` returns a `FileBatchWriter`; `DataGenerator.writeStream`
returns a `FileStreamWriter`. These are returned objects, not top-level
`rand_engine` exports. Both inherit the format, mode and option chain from
`FileWriter`; `save` completes a batch write, `trigger` configures a stream writer
and returns it, and `start` performs blocking stream writes until the timeout.

::: rand_engine.file_handlers.writer.FileWriter
    options:
      inherited_members: true

::: rand_engine.file_handlers._writer_batch.FileBatchWriter
    options:
      inherited_members: true

::: rand_engine.file_handlers._writer_stream.FileStreamWriter
    options:
      inherited_members: true
