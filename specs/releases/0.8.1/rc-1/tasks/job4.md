# Job 4 — Python-engine text methods and the column-wise assembly (wave 4, waits on Job 3)

`PyCore` bodies named by the SPEC's invariant 12 Origin: `gen_complex_distincts`, `gen_distincts_map`, `gen_distincts_multi_map`, `gen_distincts_map_prop`, and `gen_distincts_untyped` (deleted). The map family returns one array per level; `generate_first_level` assembles with `zip(cols, values)`, deleting the per-row split. `pool_draw` comes from Job 3. The hardened `test_gen_distincts_map_puts_category_first` is kept and reshaped from rows to columns. Pin edits are `test(` commits citing the SPEC approval. Owner test of every task: `tests/test_0_py_core.py`; the `test_2` goldens `distincts_map`, `distincts_multi_map`, `distincts_map_prop` and `test_golden_multi_column_draw_order` stay green with their literals.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J4.T1 | sr | AC1.4, AC5.1 | `tests/test_0_py_core.py` | RED complex_distincts: Arrow result; the CI IP pattern; integer, float, bool and big-int template parts render the 0.8.0 text; pin `:18` |
| J4.T2 | sr | AC1.4 | `rand_engine/core/_py_core.py` | REBUILD `gen_complex_distincts`: literals as Arrow scalars, small-range integer parts through a text table, one `binary_join_element_wise` pass; non-integer parts keep `astype(str)` |
| J4.T3 | sr | AC1.7, AC1.8, AC1.9, AC1.12, AC5.1 | `tests/test_0_py_core.py` | RED map family: one array per level, category first then value, weights and column order as 0.8.0, a mixed int and str level keeps `object`; pins `:163`, `:182`, `:199`, `:217`, `:237`, `:258`, `:277`, `:366` and `puts_category_first` reshaped, every literal kept |
| J4.T4 | jr | AC1.11, AC5.1 | `tests/test_0_py_core.py` | DELETE the five `gen_distincts_untyped` tests (`:131`, `:141`, `:150`, `:315`, `:323`) in a `test(` commit citing the SPEC approval |
| J4.T5 | sr | AC1.7, AC1.8, AC1.9 | `rand_engine/core/_py_core.py`, `rand_engine/main/_rand_generator.py` | REBUILD the three map methods (`rng.integers(0, len(table), size)` once, a `pool_draw` per level, the 0.8.0 draws) and `generate_first_level` to `zip(cols, values)` |
| J4.T6 | jr | AC1.11 | `rand_engine/core/_py_core.py` | DELETE `PyCore.gen_distincts_untyped`; `grep -rn gen_distincts_untyped rand_engine tests` returns 0 hits |
