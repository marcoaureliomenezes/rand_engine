# Job 5 — FR3.2 and FR3.3 the package docstring and the `trigger` annotation

**Wave:** 2 · **Waits on:** Job 1

Bugs closed: `package-docstring-contradicts-pitch`, `stream-trigger-frequency-annotated-int`. Both fixes are one line each; no body changes.

- The package docstring becomes the exact `description` that Job 1 keeps in `[project]` (the PyPI Summary). The test reads the Summary line of the `built_wheel` METADATA, the same value, so no TOML reader or new decider is added (PLAN §1.1).
- `frequency: float` matches the docstring (`_writer_stream.py` Parameters) and `docs/3_WRITING_FILES.md:95`.
- J5.T2 and J5.T3 have disjoint write sets and run in parallel after J5.T1.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J5.T1 | sr | AC3.2, AC3.3 | `tests/integrations/test_public_api.py`, `tests/test_5_files_write_stream.py` | RED, two strict-xfail tests: the first line of `rand_engine.__doc__` equals the wheel METADATA `Summary`; `typing.get_type_hints(FileStreamWriter.trigger)["frequency"] is float`. Owners: tests/integrations/test_public_api.py (AC3.2), tests/test_5_files_write_stream.py (AC3.3) |
| J5.T2 | jr | AC3.2 | `rand_engine/__init__.py`, `tests/integrations/test_public_api.py` | line 1 becomes the package description text verbatim; removes its marker. Owner: tests/integrations/test_public_api.py |
| J5.T3 | jr | AC3.3 | `rand_engine/file_handlers/_writer_stream.py`, `tests/test_5_files_write_stream.py` | `frequency: int` → `frequency: float` at `:31`; removes its marker. Owner: tests/test_5_files_write_stream.py |
