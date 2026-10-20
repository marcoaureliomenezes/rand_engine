# Job 2 — the one text-column decider (wave 2, waits on Job 1)

Foundation: `RandGenerator._column` decides "a generated text column is Arrow"; `_assign_nulls` stops dropping Arrow. Tests that pin the old text type are edited here as `test(` commits whose body cites the SPEC's operator approval (invariant 12 Origin, FR5) and swaps the container or type only; every literal value assert is kept.

Serial order: T1 then T2 (same test file), T3, T4, then T5 then T6 (same source file), T7. Each RED task precedes the implementation it pins.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC2.1 | `tests/test_2_data_generator.py` | RED: through `DataGenerator.get_df` every text method (uuid4, int_zfilled, dates, complex_distincts, the three map methods, text distincts, distincts_prop, constant, `pk`/`fk` with a text `format`) is `string[pyarrow]`; numeric, boolean, datetime and mixed-type columns keep their 0.8.0 dtype |
| J2.T2 | sr | AC2.2, AC2.3, AC2.4, AC5.1, AC5.2 | `tests/test_2_data_generator.py` | RED: `null_rate` writes `pd.NA` and keeps `string[pyarrow]`, `anomaly_rate` keeps it, `stream_dict` still emits `None`; edit the pinned asserts at `:361`, `:422`, `:437`, `:492` (object/`None` to `string[pyarrow]`/`pd.NA`; the Int8, UInt16, boolean, float64 and datetime64 rows of `:492` untouched) |
| J2.T3 | jr | AC2.1, AC5.1 | `tests/test_4_rand_specs_helpers.py` | `test(` edit of `:83-110`: the text, large_text, day32, day64 and moment columns become `string[pyarrow]`; the row with no `nothing` column keeps `object` + `None` |
| J2.T4 | sr | AC2.5, AC2.6 | `tests/test_5_file_batches_formats.py` | guard, green from the start: one seeded spec over every FR1 method whose CSV and JSON bytes hash to SHA-256 literals recorded from the 0.8.0 tree; Parquet values and BYTE_ARRAY/String type unchanged; a text column read back with `dtype_backend="pyarrow"` equals the frame (RED for the dtype half) |
| J2.T5 | jr | AC2.2 | `rand_engine/main/_rand_generator.py` | UPDATE `_assign_nulls`: delete the `or is_string_dtype(dtype)` disjunct so an `ArrowDtype` column takes the extension branch (`values[mask] = pd.NA`); net -1 line; owner `tests/test_2_data_generator.py` |
| J2.T6 | sr | AC2.1, AC2.2 | `rand_engine/main/_rand_generator.py` | ADD `_column`, the single decider: Arrow passes through; a `<U` array, list or object array of all-text values becomes `pd.ArrowDtype(pa.string())`; anything else is untouched. Non-empty rule: a zero-row or all-`None` object array is NOT converted, so the empty-schema `pa.null()` catalog type stays (pinned by the unchanged `tests/test_5_empty_schema.py:21,28`; that file joins the `W:` only if a test there changes). `generate_first_level` calls it once per column; about 8 lines; owner `tests/test_2_data_generator.py` |
| J2.T7 | pe | AC4.1 | `specs/constitution.md` | UPDATE invariant 10 verbatim from AC4.1; law text, no test |
