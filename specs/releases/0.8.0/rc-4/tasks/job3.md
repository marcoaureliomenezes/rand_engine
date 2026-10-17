# Job 3 — Atomic SQLite batch output

**Wave:** 2
**Waits on:** —
**W:** `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py`,
`rand_engine/file_handlers/writer.py`, `rand_engine/file_handlers/_writer_batch.py`,
`rand_engine/file_handlers/_writer_stream.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | sr | AC3.1–AC3.5 | `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py` | RED tests for required table; unique string, NUL-free generated labels (non-string, NUL and duplicate-label partitions refuse before output); default overwrite and append; typed round trips; quoted hostile identifiers and bound hostile values; selected-table preservation; staged overwrite rollback; append rollback/schema mismatch; unsupported values/options/modes; and `writeStream` refusal before output. |
| J3.T2 | sr | AC3.1–AC3.5 | `rand_engine/file_handlers/writer.py`, `rand_engine/file_handlers/_writer_batch.py`, `rand_engine/file_handlers/_writer_stream.py` | Add only stdlib-SQLite batch format policy and implementation: quoted identifiers without lossy string mapping, parameter-bound typed values, staged atomic overwrite retaining unrelated tables, and transactional append. Refuse file-only options and SQLite stream use before touching paths. |

`J3.T2` may not edit tests and does not expose a connection, read destination values
to generation, or add a database layer/dependency.
