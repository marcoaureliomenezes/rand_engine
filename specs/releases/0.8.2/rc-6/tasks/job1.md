# Job 1 — the file writer derives its opener from the format (wave 1)

Runs beside Jobs 2 to 5. No behaviour is new: every written file, option list and refusal message is unchanged, so the owner tests are the existing `FileHandler.to_*` cases of `tests/test_5_files_write_batch.py`, read-only here (Job 2 owns the file).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | jr | AC39.1, AC39.2 | `rand_engine/file_handlers/file_handler.py` | REBUILD `_to_file` (`:378`): drop the `opener` parameter, resolve it from `format` through `getattr(FileHandler, f"open_{format}")`; `to_csv`, `to_json`, `to_parquet` (`:403,407,411`) pass only the format. `git diff --numstat` deletes more lines than it adds. Commit `refactor(J1.T1): REBUILD _to_file — …`. Owner: the existing `to_*` cases, asserts unchanged |

Done when: `verify:`; `tests/test_5_files_write_batch.py`, `tests/test_5_files_write_stream.py` pass; `git diff <base>...HEAD --name-only` is only `file_handler.py`; `git grep -n '_to_file\b'` shows four hits, none with an opener.
