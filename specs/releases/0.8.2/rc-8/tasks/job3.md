# Job 3 — the writer Raises sections and the dead benchmark import (wave 1)

Runs beside Jobs 1 and 2. The two tasks write disjoint files.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | jr | AC53.1, AC53.2, AC53.3 | `rand_engine/file_handlers/_writer_batch.py`, `rand_engine/file_handlers/_writer_stream.py` | `docs(J3.T1)`: append the lines below to the `Raises` > `RandEngineError` block of `FileBatchWriter.save` (after `_writer_batch.py:357`) and `FileStreamWriter.start` (after `_writer_stream.py:81`), at the 8-space indent of the existing sentence; nothing else changes. Net +5 |
| J3.T2 | jr | AC51.1 (the `benchmarks/` line) | `benchmarks/comparison.py` | `chore(J3.T2)`: delete the unused `import sys` at `:12`; `git grep -nw sys -- benchmarks/comparison.py` prints nothing after. Net -1 |

`save`, three lines:

```
        If the format is not ``"csv"``, ``"json"``, ``"parquet"`` or ``"sqlite"``, an option is not documented for it, or an option value is refused (csv ``index``, ``sep`` or ``compression``; json ``orient`` or ``compression``; parquet ``compression``).
        For SQLite: a ``table`` option that is missing or not a non-empty string, any other option, a mode other than ``overwrite`` or ``append``, an append whose schema differs from the table, or a write that fails.
        If a csv or parquet column mixes types; or, appending, a parquet schema differs from the file's, a ``numFiles`` destination is not a directory, or a zip output does not hold exactly one file.
```

`start`, two lines:

```
        If the format is ``"sqlite"`` (batch only) or is not ``"csv"``, ``"json"`` or ``"parquet"``, an option is not documented for it (``numFiles`` and ``maxRowsPerBatch`` are batch options), or an option value is refused (csv ``index``, ``sep`` or ``compression``; json ``orient`` or ``compression``; parquet ``compression``).
        If a csv or parquet column mixes types.
```

Done when: `verify:`; `ruff check --select D rand_engine/file_handlers/_writer_batch.py rand_engine/file_handlers/_writer_stream.py` prints `All checks passed!`; the doctests of `rand_engine/file_handlers`, `tests/test_docs.py` and `tests/test_comparison.py` pass; `git diff --numstat <base>...HEAD -- rand_engine` shows `3 0` and `2 0` and names only the two writers.
