# Job 4 — docstring and doc accuracy (wave 1)

Runs beside Jobs 1, 2, 3 and 5. Text only; no `gen_*` body changes and no `ruff D` regression (`verify:` runs it). Job 9 waits on this job's merge, since `_writer_batch.py` and `_writer_stream.py` are measured paths.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J4.T1 | jr | AC34.1 | `rand_engine/file_handlers/_writer_batch.py`, `rand_engine/file_handlers/_writer_stream.py`, `rand_engine/main/_rand_generator.py`, `rand_engine/validators/exceptions.py` | the Raises sections (`_writer_batch.py:364`, `_writer_stream.py:82`) use the `resolve_size` wording (`data_generator.py:36`); `_rand_generator.py:37` reads "an empty unicode ndarray"; the `ColumnGenerationError` docstring (`exceptions.py:53-58`) states its three steps once. Owner: `ruff D` and the doctests in `verify:` |
| J4.T2 | jr | AC34.2 | `docs/1_DATA_GENERATOR.md` | the timezone sentence (`:91`) leaves the `dates` paragraph (`%z` with `dates` fails the directive check). Owner: `tests/test_docs.py` |
| J4.T3 | jr | AC34.3 | `CHANGELOG.md` | `:34`'s size bullet says `SparkGenerator` now takes a callable size, where 0.8.1 raised a raw `TypeError`; no other edit under `## [0.8.2]` (AC38.3). Owner: the dated-header test in `tests/test_docs.py` |

Done when: `verify:`; `tests/test_docs.py` passes.
