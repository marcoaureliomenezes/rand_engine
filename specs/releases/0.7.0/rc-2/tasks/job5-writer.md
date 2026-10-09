# Job 5 — bounded batch writer and stable sinks

**Status:** Approved

The stage rows below remain the executed historical record. The fresh J5.T4 assertion-first owner runs before either original source task. After those sources merge, J5.T5/J5.T6 preserve the disabled-batching JSON contract before J5.T1 and J5.T2 retire satisfied markers without changing an assertion:

| task | AC | `W:` | outcome |
|---|---|---|---|
| J5.T1 | AC1.1, AC1.3–AC1.6, AC4.2, AC8.7, AC9.1, AC9.3 | `tests/test_5_files_write_batch.py` | Retire writer-plan markers; owner `tests/test_5_files_write_batch.py`. A `test(...)` commit deletes only markers satisfied by J5.S2.T1. |
| J5.T2 | AC1.2, AC1.6, AC3.4 | `tests/test_5_file_batches_formats.py` | Retire adapter markers; owner `tests/test_5_file_batches_formats.py`. A `test(...)` commit deletes only markers satisfied by J5.S2.T2. |
| J5.T3 | AC1.1–AC1.6, AC3.4, AC4.2, AC8.6–AC8.7, AC9.1, AC9.3 | `specs/releases/0.7.0/rc-2/tasks/job5-writer.md` | Close writer job; owner `tests/test_5_files_write_batch.py`. After all source corrections, both marker-retirement tasks and the fixture repair are green, write terminal `done` exactly once. |
| J5.T4 | AC1.6, AC3.4, AC9.3 | `tests/test_5_empty_schema.py` | All-partitions-empty typed-schema RED; owner `tests/test_5_empty_schema.py`. Fresh assertion-first public-save tests, without strict xfail, require determinate size-zero requests to create the literal requested file count with readable zero-row typed schemas and zero generation, transform or RNG requests. Cover one-file and repeated-format positive cases plus prior-destination bytes preserved on genuinely indeterminate refusal; spy only at the external NumPy RNG boundary, with no own-module patch or source-text assertion. |
| J5.T5 | AC1.3, AC1.4, AC9.1 | `tests/test_5_file_batches_formats.py` | Disabled-batching JSON compatibility RED; owner `tests/test_5_file_batches_formats.py`. Fresh unmarked public-save assertions prove both absent and explicit `maxRowsPerBatch=None` retain the one-frame pandas JSON-lines result for a transformed heterogeneous object column, with exact literal records and one transformer call. A batching-enabled control must refuse the genuinely indeterminate schema before destination mutation. Preserve every old assertion. |
| J5.T6 | AC1.3, AC1.4, AC9.1 | `rand_engine/file_handlers/file_handler.py` `rand_engine/file_handlers/_writer_batch.py` | Restore disabled-batching JSON compatibility; owner `tests/test_5_file_batches_formats.py`. Keep one JSON session and pandas serialization: defer a single Arrow-indeterminate payload with `session.schema is None`, let the legacy one-frame path close it, and make the batching-enabled planner refuse that same indeterminate state before staging commit. No public flag, generic layer or second JSON serializer/path. |

Order: J5.T4 first; then J5.S2.T1 and J5.S2.T2 may proceed in parallel, with J5.S2.T3 independently test-only. After the original sources merge, J5.T5 → J5.T6. J5.T1 and J5.T2 marker retirement follow all owning source corrections; J5.T3 is last.

## Stage J5.S1 — RED

- Contract: exit writer/format/fixture tests fail by assertion under strict xfail markers; envelope `tests/test_5_files_write_batch.py tests/test_5_file_batches_formats.py tests/test_5_writer_fixture_paths.py`; ACs AC1.1–AC1.6, AC3.4, AC4.2, AC8.6, AC9.1, AC9.3.
- J5.S1.T1 — row-plan/transaction RED · AC1.1, AC1.3–AC1.6, AC4.2, AC9.1, AC9.3 · `W:` `tests/test_5_files_write_batch.py` · owner `tests/test_5_files_write_batch.py` · literal plan offsets, max generated frame, old unbatched cadence, destination preserved on every failure.
- J5.S1.T2 — append-format/schema RED · AC1.2, AC1.6, AC3.4 · `W:` `tests/test_5_file_batches_formats.py` · owner `tests/test_5_file_batches_formats.py` · CSV one header/compression, JSON-lines options/null, Parquet schema/null, zero-row typed files and schema drift.
- J5.S1.T3 — fixture-path RED · AC8.6 · `W:` `tests/test_5_writer_fixture_paths.py` · owner `tests/test_5_writer_fixture_paths.py` · assert the final `tmp_path` contract against the current persistent fixture under one strict marker; no fixture repair occurs in RED.

## Stage J5.S2 — rebuild batch writer

- Contract: exit all writer owners GREEN under the current two-gate source/test separation, then write this job file's terminal `done` once; ACs AC1.1–AC1.6, AC3.4, AC4.2, AC8.6, AC8.7, AC9.1, AC9.3.
- J5.S2.T1 — linear lazy plan and staged commit · AC1.1, AC1.3–AC1.6, AC3.4, AC4.2, AC8.7, AC9.1, AC9.3 · `W:` `rand_engine/file_handlers/_writer_batch.py` `rand_engine/file_handlers/writer.py` `rand_engine/main/data_generator.py` `rand_engine/validators/method_specs.py` · owner `tests/test_5_files_write_batch.py` · source-only implementation of cumulative offsets, one-frame memory, same-filesystem staging/rollback and an internal lazy `schema_def` derived from the canonical catalog plus declared specs. All-empty partitions emit typed outputs without generation, transform or RNG draws; there is no second registry, sampling or bound-method introspection.
- J5.S2.T2 — stateful existing format adapters · AC1.2, AC1.6, AC3.4 · `W:` `rand_engine/file_handlers/file_handler.py` · owner `tests/test_5_file_batches_formats.py` · source-only implementation; CSV/JSON streams and ParquetWriter hold per-file state and the CSV timezone adapter is retained.
- J5.S2.T3 — repair fixture path · AC8.6 · `W:` `tests/fixtures/f3_integrations.py` `tests/test_5_writer_fixture_paths.py` · owner `tests/test_5_writer_fixture_paths.py` · move writer outputs to pytest `tmp_path`, remove persistent repo-tree cleanup, and delete only the now-satisfied RED marker in the same GREEN task.
