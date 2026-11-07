# Job 9 — error texts, the Spark callable size, CHANGELOG (wave 3)

Waits on Job 7 (the generator files, and the user-visible validator behaviour the CHANGELOG states). T1 then T2 (one test file); T3 and T4 beside them (disjoint).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J9.T1 | sr | AC28.1 | `tests/test_3_spark_generator.py` | `test(J9.T1)`, pins green on arrival (`spark_generator.py:190-207` already does this; the hand-back says so): with a callable size, an fk whose first row has no eligible parent raises `RandEngineError` naming the column; a callable returning 0 yields an empty frame |
| J9.T2 | jr | AC21.5, AC28.3 | `tests/test_3_spark_generator.py` | `test(J9.T2)`: the text-with-none case (`:739`) and its `future.infer_string` twin (`:780-784`) become one test parametrized over the option, both partitions running, no assert removed; `seconds()` (`:234-237`) converts one way with no branch on the method, its asserts unchanged. Reviewer check: reverting the parametrization of the option drops a partition |
| J9.T3 | jr | AC27.1, AC27.2, AC28.2 | `rand_engine/main/data_generator.py`, `rand_engine/main/spark_generator.py`, `rand_engine/validators/exceptions.py` | docstring text only: the Raises sections at `data_generator.py:269,307` and `SparkGenerator.get_df` (`:149-150`) use the `resolve_size` wording (`data_generator.py:33-36`); `SparkGenerator.size` (`:118`) documents an int or a callable returning one; `exceptions.py` anomaly-dtype clause (`:12-14`) reads "the column's transformers (embedded or global)" and the `ColumnGenerationError` docstring (`:52-57`) names the method call, the conversion and the multi-column unpack as `docs/errors.md:16` does. `ruff D` and the doctests in `verify:` are the check. `docs(J9.T3)` |
| J9.T4 | jr | AC27.3, AC29.2 | `CHANGELOG.md` | `:28`'s int64 clause reads "in a numeric pool"; `:39` names 0.8.0 as the measured version; `## [0.8.2]` gains one entry per user-visible change rc-4 lands (the aware/naive start-end message, the template errors reported together). Eval, test and docstring changes get none. Owner: the dated-header test in `tests/test_docs.py` |

Done when: `verify:`; `tests/test_3_spark_generator.py`, `tests/test_docs.py` pass. Sweep: `git grep -n "size was not set" -- rand_engine docs CHANGELOG.md` prints nothing.
