# Job 5 — FR3.3 to FR3.5 numpydoc on the public surface

**Wave:** 2 · **Waits on:** Job 2

- Public surface: `DataGenerator`, `SparkGenerator`, the objects `write` and `writeStream` return (`FileBatchWriter.save`, `FileStreamWriter.trigger` and `start`, `FileWriter` options) and `RandSpecs`. `ruff --select D` reports 0 on `_writer_batch.py` and `_writer_stream.py` because ruff skips `_`-prefixed modules, so a green ruff alone diverges from the demand: one pytest over `inspect` of the public callables of the 5 objects closes it.
- Docstring only: no `gen_*` body, no `StreamHandler`, no behaviour change (AC3.5, checked on the diff); no rename (`wrapped_df_generator` and `map_methods` keep their names).
- Spark examples carry `# doctest: +SKIP` (a local session start costs 8-37 s); Spark behaviour stays proven by the suite. Each example generates <= 10^4 rows and writes under a temporary directory.
- Gate cost (measured, handoff 2026-10-14): ruff D 0.03 s; doctest of 8 prototype examples < 1 s inside the existing pytest run.
- `tests/test_docs.py` docstrings carry no AC ids (done in J8.T1 where that file is next touched).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J5.T1 | sr | AC3.3, AC3.4, AC3.6 | `tests/test_docs.py` | RED: `inspect` over the public callables of the 5 objects (incl. writer `save`, `start`, `trigger`) requires a docstring with Parameters/Returns; `doctest` runs the examples of the 6 modules. Owner: tests/test_docs.py |
| J5.T2 | jr | AC3.3, AC3.4 | `rand_engine/main/data_generator.py` | numpydoc for the 9 D hits of `DataGenerator` (class, `get_df`, `write`, `writeStream`, `stream_dict` ...) with runnable examples; no body change. Owner: tests/test_docs.py |
| J5.T3 | jr | AC3.3, AC3.4 | `rand_engine/main/spark_generator.py`, `rand_engine/file_handlers/writer.py` | numpydoc for `SparkGenerator` (7 D hits, malformed `Raises` at :18) and `FileWriter` (`format`/`mode`/`option`/`options`); Spark examples `+SKIP`. Owner: tests/test_docs.py |
| J5.T4 | jr | AC3.3, AC3.4 | `rand_engine/file_handlers/_writer_batch.py`, `rand_engine/file_handlers/_writer_stream.py` | numpydoc for `FileBatchWriter.save`, `FileStreamWriter.trigger` and `start`. Owner: tests/test_docs.py |
| J5.T5 | jr | AC3.3, AC3.4 | `rand_engine/examples/common_rand_specs.py` | numpydoc for the 10 spec factories of `RandSpecs` (D400 x10, D401, D100), `faker_pool` and `from_schema` kept. Owner: tests/test_docs.py |
| J5.T6 | sr | AC3.3 | `AGENTS.md` | repo law: the three `verify:` lines run `ruff check --select D` on the 6 modules of AC3.3 before pytest (ruling 4); the cost is stated in PLAN §3. No test (repo law; evidence: the verify: line exits 0). Owner test: none |
