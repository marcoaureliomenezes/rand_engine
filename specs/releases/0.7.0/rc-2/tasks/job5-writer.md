# Job 5 — bounded batch writer and stable sinks

**Status:** Approved

## Stage J5.S1 — RED

- Contract: exit writer/format/fixture tests fail by assertion under strict xfail markers; envelope `tests/test_5_files_write_batch.py tests/test_5_file_batches_formats.py tests/test_5_writer_fixture_paths.py tests/fixtures/f3_integrations.py`; ACs AC1.1–AC1.6, AC3.4, AC4.2, AC8.6, AC9.1, AC9.3.
- J5.S1.T1 — row-plan/transaction RED · AC1.1, AC1.3–AC1.6, AC4.2, AC9.1, AC9.3 · `W:` `tests/test_5_files_write_batch.py` · owner `tests/test_5_files_write_batch.py` · literal plan offsets, max generated frame, old unbatched cadence, destination preserved on every failure.
- J5.S1.T2 — append-format/schema RED · AC1.2, AC1.6, AC3.4 · `W:` `tests/test_5_file_batches_formats.py` · owner `tests/test_5_file_batches_formats.py` · CSV one header/compression, JSON-lines options/null, Parquet schema/null, zero-row typed files and schema drift.
- J5.S1.T3 — fixture-path RED and tests-only repair · AC8.6 · `W:` `tests/fixtures/f3_integrations.py` `tests/test_5_writer_fixture_paths.py` · owner `tests/test_5_writer_fixture_paths.py` · first observe the old persistent-path assertion RED, then make the final fixture use `tmp_path`; strict marker remains RED until Stage 2.

## Stage J5.S2 — rebuild batch writer

- Contract: exit all writer owners GREEN by marker deletion only, then write this job file's terminal `done` once; envelope `rand_engine/file_handlers/** tests/test_5_files_write_batch.py tests/test_5_file_batches_formats.py tests/test_5_writer_fixture_paths.py specs/releases/0.7.0/rc-2/tasks/job5-writer.md`; ACs AC1.1–AC1.6, AC3.4, AC4.2, AC8.6, AC8.7, AC9.1, AC9.3.
- J5.S2.T1 — linear lazy plan and staged commit · AC1.1, AC1.3–AC1.6, AC4.2, AC8.7, AC9.1, AC9.3 · `W:` `rand_engine/file_handlers/_writer_batch.py` `rand_engine/file_handlers/writer.py` `tests/test_5_files_write_batch.py` · owner `tests/test_5_files_write_batch.py` · cumulative offsets, one-frame memory, same-filesystem staging/rollback, validated controls excluded from format options.
- J5.S2.T2 — stateful existing format adapters · AC1.2, AC1.6, AC3.4 · `W:` `rand_engine/file_handlers/file_handler.py` `tests/test_5_file_batches_formats.py` · owner `tests/test_5_file_batches_formats.py` · CSV/JSON streams and ParquetWriter hold per-file state; CSV timezone adapter retained.
- J5.S2.T3 — complete fixture cleanup · AC8.6 · `W:` `tests/test_5_writer_fixture_paths.py` · owner `tests/test_5_writer_fixture_paths.py` · delete only the RED marker line associated with the already-final tests-only fixture change.
- J5.S2.T4 — close writer job · AC1.1–AC1.6, AC3.4, AC4.2, AC8.6–AC8.7, AC9.1, AC9.3 · `W:` `specs/releases/0.7.0/rc-2/tasks/job5-writer.md` · owner `tests/test_5_files_write_batch.py` · after the stage contract is green, write terminal `done` exactly once and commit `chore(tasks): done job5-writer`.
