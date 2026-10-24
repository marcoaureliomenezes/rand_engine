# Job 4 — the pandas dtype contract follows pandas (wave 2)

Serial: T1 to T6 (the test files and the two sources overlap). Rulings the `test(` commits name: the operator's "uai, se possivel ns. See if for pyarrow is faster. If it is, we use it. if no, we use pandas." plus the main thread's ruling on the four literals (T3) and on the docs assert (T6).

Scratch commands (pandas 3; `verify:` stays on the lock's pandas 2.2.3), run from the task tree, output in the commit body:

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. uv run --no-project --python 3.12 --with pandas==3.1.0 --with pyarrow==26.0.0 --with numpy --with faker --with pytest python -m pytest -q -p no:cacheprovider <files>`

Call it `P3 <files>`. RED steps: `P3` red on the named file before the implementation; GREEN: `P3 tests/` passes after T5 (Spark files need the Spark env, skip them in `P3`).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J4.T1 | sr | AC2.5 | `tests/test_6_stream_objects.py` | RED: a `dates` column with a `pd.Timestamp` transformer has a datetime dtype (not `timestamp[us][pyarrow]`) and `stream_dict` yields text; red under `P3`, green already on 2.2.3 |
| J4.T2 | jr | AC2.6 | `tests/test_5_files_write_batch.py`, `tests/test_6_stream_objects.py` | arrange steps only: the seven writer cases build their frames with an explicit `datetime64[ns]` unit; the three string-subclass cases build theirs from `object`, `StringDtype("python")` or object-category inputs; asserts unchanged; `P3` and `verify:` green |
| J4.T3 | sr | AC2.2, AC2.3 | `tests/test_0_np_core.py`, `tests/test_2_data_generator.py`, `tests/test_5_empty_schema.py`, `tests/conftest.py` | RED: one helper in `conftest.py` returns the installed pandas' natural datetime unit (`ns` on 2.x, `us` on 3.x); the four literals (`test_0_np_core.py:714` `value7`, `test_2_data_generator.py:489` `null_rate=1` dates, `test_5_empty_schema.py:213-218` both cases) take it; the empty-schema test asserts the size-0 Arrow type equals the size-4 type for naive and UTC-aware values; red under `P3` |
| J4.T4 | sr | AC2.2 | `rand_engine/validators/method_specs.py` | REBUILD `_constant_arrow_type` (`:82-93`): delete the hard-coded `ns` branch; a datetime value takes the type of the pandas -> Arrow conversion; every other value keeps `pa.scalar(value).type`; re-read its consumer (`:447`); owner `tests/test_5_empty_schema.py`; `P3` and `verify:` green; net lines negative |
| J4.T5 | sr | AC2.1, AC2.4, AC2.5, AC2.8 | `rand_engine/main/_rand_generator.py` | UPDATE `_column` (narrow pin, PLAN §1.2) and `apply_embedded_transformers` (object view); `tests/test_0_py_core.py:396-399` passes unchanged under `P3` and `verify:`; J4.T1 goes green under `P3`; `P3 tests/` has 0 failures (numeric and boolean dtypes unchanged, AC2.1); `StreamHandler` untouched (`git diff --stat` shows it absent); record every `P3` red and green output in the commit body |
| J4.T6 | jr | AC2.7 | `docs/1_DATA_GENERATOR.md`, `docs/3_WRITING_FILES.md` | `1_DATA_GENERATOR.md:252` states that a transformer's output dtype is the installed pandas' inference, and its executed `dtype == object` assert becomes `dtype == pd.Series([...]).dtype` of the transformer's plain Python result (never deleted); `3_WRITING_FILES.md:144-146` says the fraction follows the column's unit, with no "`ns` (the pandas default)"; owner `tests/test_docs.py`; green under `P3 tests/test_docs.py` and `verify:` |

Done when per task: `verify:`; `P3` over the files the change reaches; a seeded-output check that `tests/test_2_data_generator.py::test_golden_seeded_output` passes unchanged.
