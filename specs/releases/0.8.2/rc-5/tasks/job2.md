# Job 2 — one accepted-options decider per writer format, REBUILD (wave 1)

Runs beside Jobs 1, 3, 4 and 5. Order: T1, then T2 (T1 is green on arrival and pins the contract), T3 after T1 (same test file). Job 8 and Job 9 wait on this job.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC31.1 | `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py` | `test(J2.T1)`: for csv, json and parquet, an undocumented option is refused with the full literal `<format> option '<key>' is not documented; accepted: <list>` on `write…save` and on `writeStream…start`; the list is a literal in each row. Reviewer check: drop one key from `file_handler.py` `:125`, `:211` or `:293` alone, and from `:387`, `:397` or `:407` alone: each turns a row red |
| J2.T2 | sr | AC31.2 | `rand_engine/file_handlers/file_handler.py` | REBUILD: one accepted-options tuple per format; constructors and `to_csv`, `to_json`, `to_parquet` read it, and the `to_*` functions add only the writer's own keys. Messages, exception classes and lists unchanged; file net lines ≤ 0 (`git diff --numstat`). Owner: J2.T1 |
| J2.T3 | jr | AC31.3 | `tests/test_5_files_write_batch.py` | pending the operator's order (SPEC §6.1): the two json `indent` tests (`:271-281`) fold into J2.T1's json rows with option `indent`, keeping their literals and their `not path.exists()` asserts; `test(J2.T3)` quotes the order. Without it: cancelled, both tests stay |

Done when: `verify:`; `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py`, `tests/test_5_file_batches_formats.py` pass. Sweep: `git grep -nE "option '.*' is not documented" -- rand_engine` lists the one message site per format.
